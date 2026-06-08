#!/usr/bin/env python3
"""Insert the cover image + per-section concept diagrams into the COMPLETE notebooks.

Idempotent: skips an image that's already referenced. Re-run `build_student_notebooks.py`
afterwards so the student notebooks inherit the images. Image paths are relative to the
notebook location (repo root): images/<file>.
"""
from __future__ import annotations

import json
import pathlib

WS = pathlib.Path(__file__).resolve().parent.parent

# Cover image for both notebooks.
COVER = ("form_factors.png", "The AI Maturity Ladder — Five Form Factors of AI Applications")

# (locator substring in a markdown cell) -> (image file, alt text). Image is inserted
# as a new cell immediately AFTER the matched cell.
FF_SECTIONS = [
    ("# Form Factor 1 — The Chatbot", "form_factor_1_stateless.png", "Anatomy of a stateless LLM call"),
    ("## 1.1 Adding Memory", "resending_messages.png", "Memory by re-sending the whole conversation"),
    ("## 1.2 The Ceiling of a Chatbot", "form_factor_1_ceiling.png", "Where a stateless chatbot hits its limits"),
    ("# Form Factor 2 — Retrieval-Augmented Generation", "form_factor_2_rag_pipeline.png", "Anatomy of a RAG pipeline"),
    ("## 2.6 Retrieval Techniques", "form_factor_2_retrieval_techniques.png", "Five ways to retrieve from Oracle"),
    ("### Add the indexes", "hnsw_index.png", "How an HNSW index finds nearest neighbours"),
    ("### 2.6.2 Vector Search", "vector_search_embedding_space.png", "Vector search retrieves by meaning"),
    ("### 2.6.3 Attribute Filtering", "attribute_filtering.png", "Pre, in, and post filtering change your results"),
    ("### 2.6.4 Hybrid Search", "hybrid_search_rrf.png", "Reciprocal Rank Fusion merges two rankings"),
    ("### 2.6.5 Graph Retrieval", "graph_retrieval.png", "GraphRAG retrieves by following relationships"),
    ("# Form Factor 3 — The LLM-Driven Workflow", "form_factor_3_workflow.png", "Your code orchestrates the LLM"),
    ("# Form Factor 4 — The Agent", "four_faculties_of_an_agent.png", "The four faculties of an agent"),
]


def img_cell(file: str, alt: str, cid: str, width: int = 820) -> dict:
    html = f'<img src="images/{file}" alt="{alt}" width="{width}">\n'
    return {"cell_type": "markdown", "id": cid, "metadata": {}, "source": [html]}


def already_has(nb: dict, file: str) -> bool:
    return any(f"images/{file}" in "".join(c["source"]) for c in nb["cells"])


def slug(file: str) -> str:
    return "img-" + file.rsplit(".", 1)[0].replace("_", "-")


def add_cover(nb: dict) -> int:
    if already_has(nb, COVER[0]):
        return 0
    nb["cells"].insert(0, img_cell(COVER[0], COVER[1], "img-cover", width=900))
    return 1


def add_sections(nb: dict, sections) -> int:
    added = 0
    for locator, file, alt in sections:
        if already_has(nb, file):
            continue
        idx = next((i for i, c in enumerate(nb["cells"])
                    if c["cell_type"] == "markdown" and locator in "".join(c["source"])), None)
        if idx is None:
            raise SystemExit(f"locator not found: {locator!r}")
        nb["cells"].insert(idx + 1, img_cell(file, alt, slug(file)))
        added += 1
    return added


def main() -> None:
    ff = WS / "ai_maturity_form_factors_complete.ipynb"
    ev = WS / "ai_maturity_form_factors_with_evaluation_complete.ipynb"

    nb = json.loads(ff.read_text())
    n = add_sections(nb, FF_SECTIONS) + add_cover(nb)
    ff.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
    print(f"form-factors: +{n} image cell(s)")

    nb = json.loads(ev.read_text())
    n = add_cover(nb)
    ev.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
    print(f"evaluation: +{n} image cell(s)")


if __name__ == "__main__":
    main()
