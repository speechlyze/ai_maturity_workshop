"""Retrieval for Form Factor 2 (RAG) — and reused by FF3 (workflow) and FF4 (agent).

A single ``VectorStore`` embeds the Acme docs once (fastembed / ONNX, torch-free)
and serves three retrieval techniques: **vector**, **keyword**, and **hybrid (RRF)**.

It prefers **Oracle AI Database** (native ``VECTOR`` columns + Oracle Text), exactly
as in the notebook. If Oracle is unreachable it transparently falls back to an
in-memory NumPy cosine index so the whole app still runs on a laptop. The active
backend is reported to the UI via ``/api/health``.
"""
from __future__ import annotations

import array
import re
import threading
from dataclasses import dataclass

import numpy as np

# Small stopword set so free-form queries reduce to meaningful keyword terms.
_STOP = {"the", "a", "an", "and", "or", "of", "to", "in", "on", "is", "are", "do", "does",
         "i", "my", "for", "how", "what", "can", "me", "with", "be", "it", "you", "your",
         "this", "that", "from", "at", "as", "by", "if", "we", "our"}

from backend.config import settings
from backend.core.knowledge_base import DOCS


@dataclass
class Hit:
    doc_id: str
    title: str
    category: str
    score: float
    content: str = ""

    def as_dict(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "category": self.category,
            "score": round(float(self.score), 4),
            "content": self.content,
        }


def _unit(v) -> np.ndarray:
    """Normalize to a unit vector so cosine similarity is a plain dot product."""
    v = np.asarray(v, dtype=np.float32)
    n = np.linalg.norm(v)
    return v / n if n else v


class VectorStore:
    """Embeds the corpus once, then serves vector / keyword / hybrid retrieval."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.ready = False
        self.backend = "initializing"   # → "oracle" | "memory"
        self.error: str | None = None
        self.dim = 0
        self._embedder = None
        self._doc_vectors: np.ndarray | None = None
        self._conn = None
        self._by_id = {d["doc_id"]: d for d in DOCS}

    # ── lifecycle ─────────────────────────────────────────────────────────────
    def initialize(self) -> None:
        """Idempotent, thread-safe warm-up: load embeddings, then try Oracle."""
        if self.ready:
            return
        with self._lock:
            if self.ready:
                return
            from fastembed import TextEmbedding

            self._embedder = TextEmbedding(model_name=settings.embed_model)
            doc_texts = [f"{d['title']}. {d['content']}" for d in DOCS]
            self._doc_vectors = np.array(
                [_unit(v) for v in self._embedder.embed(doc_texts)], dtype=np.float32
            )
            self.dim = int(self._doc_vectors.shape[1])

            if settings.oracle_enabled:
                try:
                    self._setup_oracle()
                    self.backend = "oracle"
                except Exception as exc:  # noqa: BLE001 — any failure → memory fallback
                    self.error = str(exc).splitlines()[0][:200]
                    self.backend = "memory"
            else:
                self.backend = "memory"

            self.ready = True

    def status(self) -> dict:
        return {
            "ready": self.ready,
            "backend": self.backend,
            "dim": self.dim,
            "doc_count": len(DOCS),
            "error": self.error,
        }

    # ── query embedding ─────────────────────────────────────────────────────────
    def _query_vec(self, text: str) -> np.ndarray:
        # fastembed applies nomic's query prefix internally via query_embed.
        return _unit(next(self._embedder.query_embed(text)))

    # ── Oracle setup (mirrors the notebook DDL/ingest) ───────────────────────────
    def _setup_oracle(self) -> None:
        import oracledb

        self._conn = oracledb.connect(
            user=settings.oracle_user,
            password=settings.oracle_password,
            dsn=settings.oracle_dsn,
        )
        dim = self.dim
        table_ddl = f"""
BEGIN EXECUTE IMMEDIATE 'DROP TABLE acme_docs CASCADE CONSTRAINTS PURGE';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
CREATE TABLE acme_docs (
    doc_id    VARCHAR2(64) PRIMARY KEY,
    title     VARCHAR2(400),
    category  VARCHAR2(64),
    content   VARCHAR2(4000),
    embedding VECTOR({dim}, FLOAT32)
)
"""
        with self._conn.cursor() as cur:
            for stmt in table_ddl.split("/"):
                if stmt.strip():
                    cur.execute(stmt)
        self._conn.commit()

        with self._conn.cursor() as cur:
            try:
                cur.execute("DROP INDEX acme_text_idx")
            except oracledb.DatabaseError:
                pass
            cur.execute(
                "CREATE INDEX acme_text_idx ON acme_docs(content) "
                "INDEXTYPE IS CTXSYS.CONTEXT PARAMETERS ('SYNC (ON COMMIT)')"
            )
            try:
                cur.execute("DROP INDEX acme_vec_idx")
            except oracledb.DatabaseError:
                pass
            try:
                cur.execute(
                    "CREATE VECTOR INDEX acme_vec_idx ON acme_docs(embedding) "
                    "ORGANIZATION INMEMORY NEIGHBOR GRAPH DISTANCE COSINE "
                    "WITH TARGET ACCURACY 90 PARAMETERS (TYPE HNSW, NEIGHBORS 16, EFCONSTRUCTION 200)"
                )
            except oracledb.DatabaseError:
                pass  # exact search still works without the HNSW index
        self._conn.commit()

        rows = [
            (d["doc_id"], d["title"], d["category"], d["content"], array.array("f", vec))
            for d, vec in zip(DOCS, self._doc_vectors.astype(np.float32).tolist())
        ]
        with self._conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO acme_docs (doc_id, title, category, content, embedding) "
                "VALUES (:1, :2, :3, :4, :5)",
                rows,
            )
        self._conn.commit()

    def _embed_query_oracle(self, text: str):
        return array.array("f", self._query_vec(text).astype(np.float32).tolist())

    @staticmethod
    def _text_query(query: str) -> str:
        """Build a forgiving Oracle Text query: any meaningful term, relevance-ranked.

        Tokens are brace-escaped (so reserved words / punctuation can't break the
        parse) and joined with ACCUM, so a doc matching *any* term scores — far more
        useful for free-form input than the notebook's exact-phrase match.
        """
        tokens = re.findall(r"[A-Za-z0-9]+", query.lower())
        meaningful = [t for t in tokens if len(t) > 2 and t not in _STOP]
        chosen = meaningful or tokens[:1]
        if not chosen:
            return "{__no_match__}"
        return " ACCUM ".join("{%s}" % t for t in chosen)

    # ── public retrieval techniques ─────────────────────────────────────────────
    def search(self, query: str, technique: str = "vector", k: int = 4) -> list[Hit]:
        """Dispatch to a retrieval technique. technique ∈ vector|keyword|hybrid."""
        self.initialize()
        technique = (technique or "vector").lower()
        with self._lock:
            if self.backend == "oracle":
                fn = {
                    "vector": self._oracle_vector,
                    "keyword": self._oracle_keyword,
                    "hybrid": self._oracle_hybrid,
                }.get(technique, self._oracle_vector)
            else:
                fn = {
                    "vector": self._mem_vector,
                    "keyword": self._mem_keyword,
                    "hybrid": self._mem_hybrid,
                }.get(technique, self._mem_vector)
            return fn(query, k)

    def retrieve(self, query: str, k: int = 3) -> list[tuple[str, float]]:
        """Unified retriever used by RAG answer / workflow / agent: [(content, score)]."""
        hits = self.search(query, technique="vector", k=k)
        return [(h.content, h.score) for h in hits]

    # ── Oracle techniques ────────────────────────────────────────────────────────
    def _oracle_vector(self, query: str, k: int) -> list[Hit]:
        q = self._embed_query_oracle(query)
        sql = f"""
            SELECT doc_id, title, category, content,
                   ROUND(1 - VECTOR_DISTANCE(embedding, :q, COSINE), 4) AS similarity
            FROM acme_docs
            ORDER BY similarity DESC
            FETCH FIRST {int(k)} ROWS ONLY
        """
        with self._conn.cursor() as cur:
            cur.execute(sql, q=q)
            return [Hit(d, t, c, float(s), body) for d, t, c, body, s in cur.fetchall()]

    def _oracle_keyword(self, query: str, k: int) -> list[Hit]:
        sql = f"""
            SELECT doc_id, title, category, content, SCORE(1) AS score
            FROM acme_docs
            WHERE CONTAINS(content, :kw, 1) > 0
            ORDER BY SCORE(1) DESC
            FETCH FIRST {int(k)} ROWS ONLY
        """
        with self._conn.cursor() as cur:
            cur.execute(sql, kw=self._text_query(query))
            return [Hit(d, t, c, float(s), body) for d, t, c, body, s in cur.fetchall()]

    def _oracle_hybrid(self, query: str, k: int, per_list: int = 10, rrf_k: int = 60) -> list[Hit]:
        q = self._embed_query_oracle(query)
        sql = f"""
            WITH
            vec AS (
                SELECT doc_id, ROW_NUMBER() OVER (ORDER BY VECTOR_DISTANCE(embedding, :q, COSINE)) AS r_vec
                FROM acme_docs ORDER BY VECTOR_DISTANCE(embedding, :q, COSINE)
                FETCH FIRST {int(per_list)} ROWS ONLY
            ),
            txt AS (
                SELECT doc_id, ROW_NUMBER() OVER (ORDER BY SCORE(1) DESC) AS r_txt
                FROM acme_docs WHERE CONTAINS(content, :kw, 1) > 0
                ORDER BY SCORE(1) DESC FETCH FIRST {int(per_list)} ROWS ONLY
            ),
            fused AS (
                SELECT COALESCE(v.doc_id, t.doc_id) AS doc_id,
                       NVL(v.r_vec, 999999) AS r_vec, NVL(t.r_txt, 999999) AS r_txt
                FROM vec v FULL OUTER JOIN txt t ON t.doc_id = v.doc_id
            )
            SELECT doc_id, ROUND(1.0/(:rk + r_vec) + 1.0/(:rk + r_txt), 6) AS rrf_score
            FROM fused ORDER BY rrf_score DESC
            FETCH FIRST {int(k)} ROWS ONLY
        """
        with self._conn.cursor() as cur:
            cur.execute(sql, q=q, kw=self._text_query(query), rk=rrf_k)
            out = []
            for doc_id, rrf in cur.fetchall():
                d = self._by_id[doc_id]
                out.append(Hit(doc_id, d["title"], d["category"], float(rrf), d["content"]))
            return out

    # ── In-memory techniques (NumPy fallback) ─────────────────────────────────────
    def _mem_vector(self, query: str, k: int) -> list[Hit]:
        qv = self._query_vec(query)
        sims = self._doc_vectors @ qv  # unit vectors → cosine == dot product
        order = np.argsort(-sims)[:k]
        out = []
        for i in order:
            d = DOCS[int(i)]
            out.append(Hit(d["doc_id"], d["title"], d["category"], float(sims[int(i)]), d["content"]))
        return out

    @staticmethod
    def _term_score(query: str, doc: dict) -> float:
        terms = {t for t in query.lower().split() if len(t) > 2}
        if not terms:
            return 0.0
        haystack = f"{doc['title']} {doc['content']}".lower()
        return sum(haystack.count(t) for t in terms)

    def _mem_keyword(self, query: str, k: int) -> list[Hit]:
        scored = [(self._term_score(query, d), d) for d in DOCS]
        scored = [(s, d) for s, d in scored if s > 0]
        scored.sort(key=lambda x: -x[0])
        return [
            Hit(d["doc_id"], d["title"], d["category"], float(s), d["content"])
            for s, d in scored[:k]
        ]

    def _mem_hybrid(self, query: str, k: int, per_list: int = 10, rrf_k: int = 60) -> list[Hit]:
        vec = {h.doc_id: r for r, h in enumerate(self._mem_vector(query, per_list))}
        kw = {h.doc_id: r for r, h in enumerate(self._mem_keyword(query, per_list))}
        fused = []
        for doc_id in set(vec) | set(kw):
            rv = vec.get(doc_id, 999999)
            rt = kw.get(doc_id, 999999)
            fused.append((1.0 / (rrf_k + rv) + 1.0 / (rrf_k + rt), doc_id))
        fused.sort(key=lambda x: -x[0])
        out = []
        for score, doc_id in fused[:k]:
            d = self._by_id[doc_id]
            out.append(Hit(doc_id, d["title"], d["category"], float(score), d["content"]))
        return out


# Module-level singleton.
store = VectorStore()
