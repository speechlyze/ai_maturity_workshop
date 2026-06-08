# 🧩 TODO 8 — Retrieval metrics — recall@k and MRR

"Which retriever is best?" is unanswerable without numbers. Two classic, cheap metrics:

- **recall@k (hit@k):** did *any* relevant document appear in the top `k` results? → `1.0` or `0.0`.
  It answers "did we surface the right doc at all, within k?"
- **MRR (Mean Reciprocal Rank):** `1 / rank` of the *first* relevant document (rank 1 → 1.0,
  rank 2 → 0.5, rank 3 → 0.33…), or `0.0` if none was retrieved. It rewards putting the right doc
  *higher*, not just *somewhere*.

### What to implement
- `hit_at_k(retrieved, relevant, k)` → `float(any(d in set(relevant) for d in retrieved[:k]))`.
- `mrr(retrieved, relevant)` → loop over `retrieved` with a 1-based index; return `1.0 / i` at the
  first doc that's in `set(relevant)`; return `0.0` if none match.

> 💡 These are computed in plain Python here so you can see exactly what the platform metrics in
> Part 1.1 are measuring under the hood.

## ✅ Solution

Replace the placeholder cell with this, then run the **`✅ TODO 8 check`** cell:

```python
import pandas as pd


def hit_at_k(retrieved, relevant, k):
    return float(any(d in set(relevant) for d in retrieved[:k]))


def mrr(retrieved, relevant):
    for i, d in enumerate(retrieved, 1):
        if d in set(relevant):
            return 1.0 / i
    return 0.0


def score_retriever(fn):
    rows = [(hit_at_k(fn(e["question"]), e["relevant"], 1),
             hit_at_k(fn(e["question"]), e["relevant"], 3),
             mrr(fn(e["question"]), e["relevant"])) for e in RETRIEVAL_EVALSET]
    arr = np.array(rows)
    return {"recall@1": arr[:, 0].mean(), "recall@3": arr[:, 1].mean(), "MRR": arr[:, 2].mean()}


comparison = pd.DataFrame({
    "keyword": score_retriever(retr_keyword),
    "vector": score_retriever(retr_vector),
    "hybrid": score_retriever(retr_hybrid),
}).T.round(3)
print(comparison)
```

_Generated from the complete notebook — this is the exact reference implementation._
