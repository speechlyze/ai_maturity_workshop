# 🧩 TODO 10 — Write LangSmith evaluators

A LangSmith **evaluator** is just a function with a fixed signature — `(inputs, outputs,
reference_outputs)` — that returns `{"key": <metric name>, "score": <number>}`. `outputs` is what
your system produced; `reference_outputs` is the gold label from the dataset. LangSmith calls your
evaluator on every example and aggregates the scores.

### What to implement
Two exact-match evaluators for the classifier:
- `category_match(...)` → `{"key": "category_match", "score": float(outputs["category"] ==
  reference_outputs["category"])}`.
- `urgency_match(...)` → the same, comparing `"urgency"` with key `"urgency_match"`.

`float(True)` is `1.0` and `float(False)` is `0.0`, so a boolean comparison is all you need.

> 💡 The `key` is the label that shows up as a column in the LangSmith experiment view — name it
> for what it measures.

## ✅ Solution

Replace the placeholder cell with this, then run the **`✅ TODO 10 check`** cell:

```python
CLASSIFY_EVALSET = [
    {"message": "I was charged twice for my Pro seats this month.",          "category": "billing",         "urgency": "high"},
    {"message": "The API returns a 500 error on the /v1/sync endpoint.",     "category": "technical",       "urgency": "high"},
    {"message": "How do I add a teammate to my workspace?",                  "category": "account",         "urgency": "low"},
    {"message": "It would be great if you supported exporting to Parquet.",  "category": "feature_request", "urgency": "low"},
    {"message": "Just saying thanks, the product is great!",                 "category": "other",           "urgency": "low"},
    {"message": "Webhooks stopped firing and it's blocking our launch.",     "category": "technical",       "urgency": "high"},
]


def classify_target(inputs: dict) -> dict:
    return classify(inputs["message"])


def category_match(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    return {"key": "category_match", "score": float(outputs["category"] == reference_outputs["category"])}


def urgency_match(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    return {"key": "urgency_match", "score": float(outputs["urgency"] == reference_outputs["urgency"])}


ensure_dataset(
    "acme-classification",
    [{"inputs": {"message": e["message"]}, "outputs": {"category": e["category"], "urgency": e["urgency"]}}
     for e in CLASSIFY_EVALSET],
    description="Acme Cloud support messages with gold category + urgency labels.",
)

classify_experiment = ls.evaluate(
    classify_target,
    data="acme-classification",
    evaluators=[category_match, urgency_match],
    experiment_prefix="workflow-classifier",
    max_concurrency=4,
)
print("Classifier experiment complete. Accuracy:")
print(classify_experiment.to_pandas()[["feedback.category_match", "feedback.urgency_match"]].mean())
```

_Generated from the complete notebook — this is the exact reference implementation._
