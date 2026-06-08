#!/usr/bin/env python3
"""Pre-seed the BEIR `scifact` benchmark (corpus + embeddings) into Oracle.

Embedding ~2,000 scientific abstracts with fastembed is the slow step of Part 4
of the evaluation notebook (`ai_maturity_form_factors_with_evaluation_*.ipynb`) —
~11 minutes on a Codespaces-sized box. To avoid paying that even once per
Codespace, the precomputed corpus + vectors are committed to the repo as
`data/beir_scifact_seed.npz`; this script loads that artifact and does a plain
bulk INSERT (a few seconds) instead of calling fastembed.

`postCreate.sh` runs this after building the acme_docs schema, so `beir_docs`
lands in the persistent `oracle-data` volume and the notebook skips straight to
evaluation. The script is **idempotent** and **self-contained** (no `backend`
import), so it can run before the app is ever started.

Three seed paths, fastest first:
  1. `beir_docs` already populated            → do nothing.
  2. data/beir_scifact_seed.npz present        → bulk INSERT from the artifact.   ← Codespaces
  3. neither                                   → download scifact + embed + ingest,
                                                 then write the artifact for next time.

Regenerate the artifact (e.g. after changing the corpus subset or embed model):
    python scripts/seed_beir.py --export      # reads a live beir_docs → writes the .npz

⚠️  The corpus-subset selection in `load_corpus_subset()` MUST stay in lock-step
with the notebook (`N_QUERIES`, `MAX_CORPUS`, the doc text format
`f"{title}. {content[:1000]}"`, the unit-normalized `nomic-embed-text-v1.5`
vectors, and the byte-truncation of title/content). The notebook compares the
live row count against its own deterministic `beir_docs_data` length; if these
drift it rebuilds from scratch — correct, just slower.
"""
from __future__ import annotations

import array
import os
import pathlib
import sys
import time

import numpy as np

# ── Must match the notebook's Part 4 constants ───────────────────────────────
N_QUERIES = 60        # scifact has ~300 test queries; cap for a snappy run
MAX_CORPUS = 2000     # scifact has 5,183 docs; cap for memory/runtime
EMBED_MODEL = os.environ.get("AIML_EMBED_MODEL", "nomic-ai/nomic-embed-text-v1.5")

WS = pathlib.Path(__file__).resolve().parent.parent
ARTIFACT = WS / "data" / "beir_scifact_seed.npz"


def _unit(v):
    """Normalize to a unit vector so cosine similarity is a plain dot product."""
    v = np.asarray(v, dtype=np.float32)
    n = np.linalg.norm(v)
    return v / n if n else v


def connect():
    """Connect to Oracle, retrying while the container warms up (Codespaces)."""
    import oracledb

    retries = int(os.environ.get("ORACLE_CONNECT_RETRIES", "20"))
    delay = float(os.environ.get("ORACLE_CONNECT_DELAY", "4"))
    last = None
    for attempt in range(1, max(1, retries) + 1):
        try:
            return oracledb.connect(
                user=os.environ.get("ORACLE_USER", "VECTOR"),
                password=os.environ.get("ORACLE_PASSWORD", "VectorPwd_2025"),
                dsn=os.environ.get("ORACLE_DSN", "localhost:1521/FREEPDB1"),
            )
        except Exception as exc:  # noqa: BLE001
            last = exc
            print(f"  Oracle connect attempt {attempt}/{retries} failed: "
                  f"{str(exc).splitlines()[0]}")
            if attempt < retries:
                time.sleep(delay)
    raise last if last else RuntimeError("Oracle connect failed")


def beir_count(conn) -> int:
    """Rows in beir_docs, or 0 if the table doesn't exist yet (ORA-00942)."""
    import oracledb

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM beir_docs")
            return int(cur.fetchone()[0])
    except oracledb.DatabaseError:
        return 0


def create_table_and_index(conn, bdim: int) -> None:
    """(Re)create beir_docs + its Oracle Text index. Shared by both build paths."""
    import oracledb

    ddl = f"""
BEGIN EXECUTE IMMEDIATE 'DROP TABLE beir_docs CASCADE CONSTRAINTS PURGE';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
CREATE TABLE beir_docs (doc_id VARCHAR2(64) PRIMARY KEY, title VARCHAR2(1000),
    content VARCHAR2(4000), embedding VECTOR({bdim}, FLOAT32))
"""
    with conn.cursor() as cur:
        for stmt in ddl.split("/"):
            if stmt.strip():
                cur.execute(stmt)
        try:
            cur.execute("DROP INDEX beir_text_idx")
        except oracledb.DatabaseError:
            pass
        cur.execute("CREATE INDEX beir_text_idx ON beir_docs(content) "
                    "INDEXTYPE IS CTXSYS.CONTEXT PARAMETERS ('SYNC (ON COMMIT)')")


def _insert_rows(conn, rows) -> None:
    """rows = [(doc_id, title, content, vector_list), ...]. Byte-safe truncation."""
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO beir_docs (doc_id, title, content, embedding) VALUES (:1, :2, :3, :4)",
            [(cid,
              t.encode("utf-8")[:990].decode("utf-8", "ignore"),
              x.encode("utf-8")[:3900].decode("utf-8", "ignore"),
              array.array("f", v))
             for cid, t, x, v in rows],
        )
    conn.commit()


# ── Path 2: load the committed artifact (the fast path used in Codespaces) ────
def ingest_from_artifact(conn) -> None:
    print(f"▸ Loading precomputed embeddings from {ARTIFACT.relative_to(WS)} …")
    data = np.load(ARTIFACT)
    doc_ids, titles, contents = data["doc_ids"], data["titles"], data["contents"]
    vectors = data["vectors"].astype(np.float32)
    bdim = int(vectors.shape[1])
    print(f"  {len(doc_ids)} docs, VECTOR dim={bdim} — bulk inserting (no embedding)…")
    create_table_and_index(conn, bdim)
    _insert_rows(conn, zip(map(str, doc_ids), map(str, titles), map(str, contents), vectors.tolist()))
    print(f"✓ Seeded {len(doc_ids)} BEIR docs from the artifact (VECTOR dim={bdim}).")


# ── Path 3: download scifact + embed from scratch (no artifact present) ───────
def load_corpus_subset():
    """Deterministically select the scifact subset. Mirrors the notebook exactly."""
    from datasets import load_dataset

    corpus = load_dataset("BeIR/scifact", "corpus", split="corpus")
    queries = load_dataset("BeIR/scifact", "queries", split="queries")
    qrels = load_dataset("BeIR/scifact-qrels", split="test")

    qtext = {str(q["_id"]): (q["text"] or "") for q in queries}
    qrels_by_q: dict[str, dict[str, int]] = {}
    for r in qrels:
        qrels_by_q.setdefault(str(r["query-id"]), {})[str(r["corpus-id"])] = int(r["score"])

    corpus_by_id = {str(d["_id"]): d for d in corpus}
    test_qids = [qid for qid in qrels_by_q if qid in qtext][:N_QUERIES]

    relevant = {d for qid in test_qids for d in qrels_by_q[qid] if d in corpus_by_id}
    distractors = [cid for cid in corpus_by_id if cid not in relevant]
    keep = list(relevant) + distractors
    if MAX_CORPUS:
        keep = keep[: max(MAX_CORPUS, len(relevant))]
    return [(cid, corpus_by_id[cid]["title"], corpus_by_id[cid]["text"] or "") for cid in keep], len(relevant)


def build_and_embed(conn) -> None:
    print(f"▸ No artifact at {ARTIFACT.relative_to(WS)} — loading BEIR scifact "
          f"(N_QUERIES={N_QUERIES}, MAX_CORPUS={MAX_CORPUS})…")
    beir_docs_data, n_rel = load_corpus_subset()
    print(f"  {len(beir_docs_data)} corpus docs ({n_rel} relevant + "
          f"{len(beir_docs_data) - n_rel} distractors)")

    print(f"▸ Embedding with {EMBED_MODEL} (batch_size=8 — the slow step)…")
    from fastembed import TextEmbedding

    embedder = TextEmbedding(model_name=EMBED_MODEL)
    vectors = np.array(
        [_unit(v) for v in embedder.embed(
            [f"{t}. {x[:1000]}" for _, t, x in beir_docs_data], batch_size=8)],
        dtype=np.float32,
    )
    bdim = int(vectors.shape[1])

    print(f"▸ Creating beir_docs (VECTOR dim={bdim}) + text index, ingesting…")
    create_table_and_index(conn, bdim)
    _insert_rows(conn, [(cid, t, x, v) for (cid, t, x), v in zip(beir_docs_data, vectors.tolist())])
    print(f"✓ Seeded {len(beir_docs_data)} BEIR docs into Oracle (VECTOR dim={bdim}).")

    # Persist the artifact so future seeds (and a `git add`) skip embedding entirely.
    write_artifact(
        [c for c, _, _ in beir_docs_data],
        [t for _, t, _ in beir_docs_data],
        [x for _, _, x in beir_docs_data],
        vectors,
    )


# ── Artifact I/O ──────────────────────────────────────────────────────────────
def write_artifact(doc_ids, titles, contents, vectors) -> None:
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        ARTIFACT,
        doc_ids=np.array(doc_ids, dtype=object).astype("U"),
        titles=np.array(titles, dtype=object).astype("U"),
        contents=np.array(contents, dtype=object).astype("U"),
        vectors=np.asarray(vectors, dtype=np.float32),
    )
    size_mb = ARTIFACT.stat().st_size / 1e6
    print(f"✓ Wrote {ARTIFACT.relative_to(WS)} ({len(doc_ids)} docs, {size_mb:.1f} MB).")


def export_from_table(conn) -> int:
    """Read a live beir_docs table and write the committed artifact."""
    with conn.cursor() as cur:
        cur.execute("SELECT doc_id, title, content, embedding FROM beir_docs ORDER BY doc_id")
        ids, titles, contents, vecs = [], [], [], []
        for doc_id, title, content, emb in cur:
            ids.append(doc_id)
            titles.append(title or "")
            contents.append(content or "")
            vecs.append(np.asarray(list(emb), dtype=np.float32))
    if not ids:
        print("  beir_docs is empty — nothing to export. Seed it first.")
        return 1
    write_artifact(ids, titles, contents, np.vstack(vecs))
    return 0


def main() -> int:
    if "--export" in sys.argv:
        conn = connect()
        try:
            return export_from_table(conn)
        finally:
            conn.close()

    try:
        conn = connect()
    except Exception as exc:  # noqa: BLE001 — Oracle optional; notebook can self-build
        print(f"  Oracle unreachable — skipping BEIR seed ({str(exc).splitlines()[0]}).")
        print("  The evaluation notebook will build beir_docs on first run.")
        return 0

    try:
        existing = beir_count(conn)
        if existing >= 1:
            print(f"✓ beir_docs already populated ({existing} rows) — nothing to do.")
        elif ARTIFACT.exists():
            ingest_from_artifact(conn)
        else:
            build_and_embed(conn)
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
