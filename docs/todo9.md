# 🧩 TODO 9 — LLM-as-judge with structured output

How do you score a free-text answer where wording varies but meaning matters? You can't string-match.
**LLM-as-judge** uses a model to grade an output against a rubric — and by pinning the response to a
schema (a numeric `score` + a `reason`), the verdict is machine-readable and consistent.

### What to implement
Write `claude_judge(rubric, material)` — the shared judge used by both `correctness` and
`groundedness` below it:
1. Call the model with the **rubric as the system prompt** and the **material to grade as the user
   message**, constrained to `JUDGE_SCHEMA`:
   `client.messages.create(model=MODEL, max_tokens=400, system=rubric,
   messages=[{"role": "user", "content": material}],
   output_config={"format": {"type": "json_schema", "schema": JUDGE_SCHEMA}})`.
2. Parse and return: `return json.loads(text_of(resp))` → `{"score": ..., "reason": ...}`.

It's the same structured-output technique as TODO 4 — here applied to *evaluation* instead of
production.

> 💡 A judge is just another LLM call. Keep its rubric tight and binary (score 1 or 0) so the
> grades are stable enough to compare experiments.

## ✅ Solution

Replace the placeholder cell with this, then run the **`✅ TODO 9 check`** cell:

```python
JUDGE_SCHEMA = {
    "type": "object",
    "properties": {"score": {"type": "number"}, "reason": {"type": "string"}},
    "required": ["score", "reason"],
    "additionalProperties": False,
}


def claude_judge(rubric: str, material: str) -> dict:
    resp = client.messages.create(
        model=MODEL, max_tokens=400, system=rubric,
        messages=[{"role": "user", "content": material}],
        output_config={"format": {"type": "json_schema", "schema": JUDGE_SCHEMA}},
    )
    return json.loads(text_of(resp))


def correctness(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    rubric = ("You grade a support answer against a reference. Return score 1 if the answer is "
              "factually consistent with the reference (same key facts; wording may differ), else 0. "
              'Respond as JSON {"score": 0 or 1, "reason": "..."}.')
    material = (f"Question: {inputs['question']}\n\nReference answer: {reference_outputs['reference']}\n\n"
               f"Answer to grade: {outputs['answer']}")
    v = claude_judge(rubric, material)
    return {"key": "correctness", "score": float(v["score"]), "comment": v["reason"]}


def groundedness(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    rubric = ("You check for hallucinations. Return score 1 if EVERY factual claim in the answer is "
              "directly supported by the provided context, else 0. "
              'Respond as JSON {"score": 0 or 1, "reason": "..."}.')
    material = f"Context:\n{outputs['context']}\n\nAnswer:\n{outputs['answer']}"
    v = claude_judge(rubric, material)
    return {"key": "groundedness", "score": float(v["score"]), "comment": v["reason"]}


# Sanity-check the judge directly (works without LangSmith) before running the experiment:
print(correctness({"question": "Pro rate limit?"},
                  {"answer": "Pro allows 1,000 requests/minute."},
                  {"reference": "The Pro plan allows 1,000 requests per minute."}))
```

_Generated from the complete notebook — this is the exact reference implementation._
