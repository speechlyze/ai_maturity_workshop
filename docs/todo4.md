# 🧩 TODO 4 — Reliable JSON with structured output

Workflows are built from steps your code can *depend on*. Free-form text ("This looks like a
billing issue, probably urgent…") is hard to branch on. **Structured output** forces the model to
return JSON that matches a schema you define — so the next step can trust `info["category"]`.

### What to implement
Write `classify(message)` to call the model with a JSON-schema constraint and parse the result:
1. `client.messages.create(model=MODEL, max_tokens=512, system="Classify the incoming Acme Cloud
   support message.", messages=[{"role": "user", "content": message}],
   output_config={"format": {"type": "json_schema", "schema": CLASSIFY_SCHEMA}})`.
2. The response text is guaranteed valid JSON for the schema — parse and return it:
   `return json.loads(text_of(response))`.

`CLASSIFY_SCHEMA` (defined just above) requires `category`, `urgency`, and `summary`.

> 💡 `output_config` makes the model's output *conform* to your schema. No regexes, no "please
> respond in JSON" pleading, no parse-and-pray.

## ✅ Solution

Replace the placeholder cell with this, then run the **`✅ TODO 4 check`** cell:

```python
def classify(message: str) -> dict:
    """Step 1: return {category, urgency, summary} as validated JSON."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        system="Classify the incoming Acme Cloud support message.",
        messages=[{"role": "user", "content": message}],
        output_config={"format": {"type": "json_schema", "schema": CLASSIFY_SCHEMA}},
    )
    return json.loads(text_of(response))


classify("I've been double-charged for my Pro seats this month and need this fixed before our board demo tomorrow.")
```

_Generated from the complete notebook — this is the exact reference implementation._
