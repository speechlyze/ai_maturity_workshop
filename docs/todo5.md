# 🧩 TODO 5 — Orchestrate the workflow pipeline

This is the heart of the **workflow** form factor: *your code* — not the model — decides the
sequence. The model fills in each step; you wire them together and add the checks. The pipeline is
fixed and predictable: **classify → route → retrieve → draft → review (and maybe revise)**.

### What to implement
Write `handle_support_message(message, max_revisions)`:
1. **Classify** — `info = classify(message)`.
2. **Route (your logic)** — flag for a human when it's urgent billing:
   `escalate = info["category"] == "billing" and info["urgency"] == "high"`.
3. **Retrieve** — reuse RAG: `hits = retrieve(message, k=3)` and build a numbered `context`.
4. **Draft** — `draft = draft_reply(message, context)`.
5. **Review / revise loop** — up to `max_revisions + 1` times: `verdict = review(message, draft,
   context)`; if `verdict["approved"]`, stop; otherwise re-draft, feeding the reviewer's
   `feedback` back into the context.
6. **Return** `{"classification": info, "escalated": escalate, "reply": draft}`.

> 💡 Compare this with Form Factor 4: here *you* hard-code the steps. There, the model chooses
> them. Workflows trade flexibility for reliability — use them when the steps are known.

## ✅ Solution

Replace the placeholder cell with this, then run the **`✅ TODO 5 check`** cell:

```python
def handle_support_message(message: str, max_revisions: int = 1) -> dict:
    # Step 1 — classify (LLM)
    info = classify(message)
    print(f"① classified: {info['category']} / urgency={info['urgency']}")

    # Step 2 — route (your code). High-urgency billing gets flagged for a human.
    escalate = info["category"] == "billing" and info["urgency"] == "high"
    if escalate:
        print("② routing: flagged for human follow-up (urgent billing)")

    # Step 3 — retrieve (RAG, reused from Form Factor 2)
    hits = retrieve(message, k=3)
    context = "\n".join(f"[{i + 1}] {doc}" for i, (doc, _) in enumerate(hits))
    print(f"③ retrieved {len(hits)} docs")

    # Step 4 — draft (LLM)
    draft = draft_reply(message, context)

    # Step 5 — review-and-revise gate (your code controls the loop)
    for attempt in range(max_revisions + 1):
        verdict = review(message, draft, context)
        print(f"④ review attempt {attempt + 1}: approved={verdict['approved']}")
        if verdict["approved"]:
            break
        print(f"   ↳ revising: {verdict['feedback']}")
        draft = draft_reply(
            message,
            context + f"\n\nReviewer feedback to address: {verdict['feedback']}",
        )

    return {"classification": info, "escalated": escalate, "reply": draft}


result = handle_support_message(
    "I've been double-charged for my Pro seats this month and need this fixed before our board demo tomorrow."
)
print("\n--- Final reply ---\n" + result["reply"])
```

_Generated from the complete notebook — this is the exact reference implementation._
