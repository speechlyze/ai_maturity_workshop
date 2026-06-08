#!/usr/bin/env python3
"""Generate the *student* notebooks + docs/todoN.md from the complete notebooks.

Non-destructive: the existing `*.ipynb` stay as the COMPLETE reference. For each
target cell we emit, into `<stem>_student.ipynb`:
  1. a markdown pointer cell  → links to docs/todoN.md
  2. a placeholder code cell  → raises NotImplementedError (the blank to fill)
  3. an assert "check" cell    → gates progress until the student's code is correct
The solution snippet written into each docs/todoN.md is the *real* original cell
source, so docs and code can never drift. Re-run any time to regenerate.
"""
from __future__ import annotations

import json
import pathlib

WS = pathlib.Path(__file__).resolve().parent.parent
DOCS = WS / "docs"
DOCS.mkdir(exist_ok=True)

POINTER = """\
### 🧩 TODO {num} — {title}

The code in the next cell has been removed. Open **[`docs/todo{num}.md`](docs/todo{num}.md)** \
for a guided explanation and the solution snippet, then replace the placeholder.

Run the **`✅ TODO {num} check`** cell right after — it must pass before you continue.\
"""

# Each spec: which cell to blank (locator = a unique substring of its source),
# the placeholder stub, the assert check, and the teaching prose for the doc.
SPECS: list[dict] = [
    # ───────────────────────── Form-factors notebook ─────────────────────────
    {
        "nb": "ff", "num": 1, "title": "Give the chatbot a memory",
        "img": "resending_messages.png", "img_alt": "Memory by re-sending the whole conversation",
        "locator": "class Chatbot:",
        "stub": '''class Chatbot:
    """A multi-turn chatbot. The 'memory' is just a growing list of messages we resend."""

    def __init__(self, system: str = "You are a helpful assistant."):
        self.system = system
        self.history: list[dict] = []

    def send(self, user_message: str) -> str:
        # 🧩 TODO 1 — make this multi-turn. See docs/todo1.md
        raise NotImplementedError("Complete TODO 1 — open docs/todo1.md")
''',
        "check": '''# ✅ TODO 1 check — do not edit. This must pass before you continue.
_bot = Chatbot()
_r = _bot.send("Say hello in exactly one word.")
assert isinstance(_r, str) and _r.strip(), "send() should return a non-empty string reply"
assert len(_bot.history) == 2, "history should hold the user message AND the assistant reply"
assert _bot.history[0]["role"] == "user" and _bot.history[1]["role"] == "assistant", \\
    "record both sides of the turn, in order (user first, then assistant)"
print("✓ TODO 1 complete — the chatbot now remembers the conversation.")
''',
        "teach": """\
A bare LLM call is **stateless** — the model sees only what you send in that one request and
remembers nothing afterwards. So how does a chatbot "remember" your name from three turns ago?

**It doesn't — you do.** The trick is to keep a running list of every message (yours and the
model's) and *re-send the whole list* on every turn. The growing `self.history` list **is** the
memory. The model re-reads the entire conversation each time and continues from there.

### What to implement
Fill in `Chatbot.send(user_message)` so that it:
1. **Appends** the user's message to `self.history` as `{"role": "user", "content": user_message}`.
2. **Calls** the API with the *entire* history: `client.messages.create(model=MODEL,
   max_tokens=MAX_TOKENS, system=self.system, messages=self.history)`.
3. **Extracts** the text with the `text_of(...)` helper.
4. **Appends** the reply to `self.history` as `{"role": "assistant", "content": reply}` — this is
   the step that makes the *next* turn aware of this one.
5. **Returns** the reply.

> 💡 Forget step 4 and the bot becomes an amnesiac — every turn would start from scratch.""",
    },
    {
        "nb": "ff", "num": 2, "title": "Semantic search with Oracle vectors",
        "img": "vector_search_embedding_space.png", "img_alt": "Vector search retrieves by meaning",
        "locator": "def vector_search(query: str, k: int = 5):",
        "stub": '''def vector_search(query: str, k: int = 5):
    # 🧩 TODO 2 — semantic (vector) search in Oracle AI Database. See docs/todo2.md
    raise NotImplementedError("Complete TODO 2 — open docs/todo2.md")
''',
        "check": '''# ✅ TODO 2 check — do not edit.
_rows, _cols = vector_search("What is the Pro plan API rate limit?", k=3)
assert _rows, "vector_search should return some rows"
assert _rows[0][0] == "rate_limits", f"the closest doc should be 'rate_limits', got {_rows[0][0]!r}"
print("✓ TODO 2 complete — vector search ranks the right document first.")
''',
        "teach": """\
Keyword search matches *words*. **Vector search** matches *meaning*: every document was embedded
into a 768-dimensional vector, and a question that means the same thing lands nearby — even with
no shared words. Oracle AI Database stores those vectors in a native `VECTOR` column and ranks
them with `VECTOR_DISTANCE`.

### What to implement
Write `vector_search(query, k)` to:
1. **Embed the query** with the *same* model used for the documents: `q = embed_query(query)`.
2. Run SQL that scores every row by cosine similarity and takes the top `k`:
   - select `doc_id, title, category` and `ROUND(1 - VECTOR_DISTANCE(embedding, :q, COSINE), 4)`
     as the similarity (distance → similarity is `1 - distance`),
   - `ORDER BY similarity DESC FETCH FIRST k ROWS ONLY`.
3. Execute it (`cur.execute(sql, q=q)`) and **return `(rows, column_names)`** — return
   `cur.fetchall()` and `[d[0] for d in cur.description]`.

> 💡 Embedding the query with a *different* model than the documents is the #1 RAG bug — the two
> vector spaces don't line up and similarity becomes meaningless.""",
    },
    {
        "nb": "ff", "num": 3, "title": "A grounded, cited RAG answer",
        "img": "form_factor_2_rag_pipeline.png", "img_alt": "Anatomy of a RAG pipeline",
        "locator": "def rag_answer(query: str, k: int = 3) -> str:",
        "stub": '''def rag_answer(query: str, k: int = 3) -> str:
    # 🧩 TODO 3 — retrieve, build a numbered context, then generate a cited answer. See docs/todo3.md
    raise NotImplementedError("Complete TODO 3 — open docs/todo3.md")
''',
        "check": '''# ✅ TODO 3 check — do not edit.
_ans = rag_answer("What is the exact API rate limit, in requests per minute, on Acme Cloud's Pro plan?")
assert isinstance(_ans, str) and _ans.strip(), "rag_answer should return a non-empty string"
assert ("1,000" in _ans) or ("1000" in _ans), "the grounded answer should contain the Pro-plan limit (1,000)"
print("✓ TODO 3 complete — the answer is grounded in your documents.")
''',
        "teach": """\
**RAG = Retrieve, then Generate.** Instead of hoping the model knows your private facts, you fetch
the relevant documents and hand them to the model *inside the prompt*, with strict instructions to
answer **only** from that material and to **cite** its sources. This grounds the answer in real
data and makes it auditable.

### What to implement
Write `rag_answer(query, k)` to:
1. **Retrieve** the top-k passages: `hits = retrieve(query, k)` (each hit is `(doc, score)`).
2. **Build a numbered context** so the model can cite by number:
   `context = "\\n".join(f"[{i+1}] {doc}" for i, (doc, _) in enumerate(hits))`.
3. **Compose a system prompt** that includes the context and says: answer using ONLY the context,
   cite with bracketed numbers like `[1]`, and admit when the answer isn't present.
4. **Call the model** with that system prompt and the user's `query`, and **return** `text_of(response)`.

> 💡 The instruction "if it's not in the context, say you don't have it" is what turns a
> confident hallucinator into a trustworthy assistant.""",
    },
    {
        "nb": "ff", "num": 4, "title": "Reliable JSON with structured output",
        "locator": "def classify(message: str) -> dict:",
        "stub": '''def classify(message: str) -> dict:
    # 🧩 TODO 4 — classify the message into validated JSON. See docs/todo4.md
    raise NotImplementedError("Complete TODO 4 — open docs/todo4.md")
''',
        "check": '''# ✅ TODO 4 check — do not edit.
_info = classify("I've been double-charged for my Pro seats and need this fixed before our demo tomorrow.")
assert set(_info) >= {"category", "urgency", "summary"}, "classify must return category, urgency, summary"
assert _info["category"] == "billing", f"a double-charge is a billing issue, got {_info['category']!r}"
assert _info["urgency"] in {"low", "medium", "high"}, "urgency must be one of the allowed values"
print("✓ TODO 4 complete — structured output gives reliable JSON:", _info)
''',
        "teach": """\
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
> respond in JSON" pleading, no parse-and-pray.""",
    },
    {
        "nb": "ff", "num": 5, "title": "Orchestrate the workflow pipeline",
        "img": "form_factor_3_workflow.png", "img_alt": "Your code orchestrates the LLM",
        "locator": "def handle_support_message(message: str, max_revisions: int = 1) -> dict:",
        "stub": '''def handle_support_message(message: str, max_revisions: int = 1) -> dict:
    # 🧩 TODO 5 — orchestrate: classify → route → retrieve → draft → review/revise. See docs/todo5.md
    raise NotImplementedError("Complete TODO 5 — open docs/todo5.md")
''',
        "check": '''# ✅ TODO 5 check — do not edit.
_res = handle_support_message(
    "I've been double-charged for my Pro seats and need this fixed before our board demo tomorrow."
)
assert set(_res) >= {"classification", "escalated", "reply"}, "result needs classification, escalated, reply"
assert _res["classification"]["category"] == "billing", "should classify as billing"
assert _res["escalated"] is True, "urgent billing should be escalated for a human"
assert isinstance(_res["reply"], str) and _res["reply"].strip(), "there must be a final reply"
print("✓ TODO 5 complete — your code orchestrated the whole pipeline.")
''',
        "teach": """\
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
> them. Workflows trade flexibility for reliability — use them when the steps are known.""",
    },
    {
        "nb": "ff", "num": 6, "title": "Give the agent a tool",
        "img": "four_faculties_of_an_agent.png", "img_alt": "The four faculties of an agent",
        "locator": "async def search_docs(args):",
        "stub": '''@tool(
    "search_docs",
    "Search the Acme Cloud documentation. Use this whenever the user asks about Acme "
    "Cloud's plans, pricing, limits, or features.",
    {"query": str},
)
async def search_docs(args):
    # 🧩 TODO 6 — call the RAG retriever and return tool content. See docs/todo6.md
    raise NotImplementedError("Complete TODO 6 — open docs/todo6.md")
''',
        "check": '''# ✅ TODO 6 check — do not edit.
import asyncio as _asyncio
assert getattr(search_docs, "name", None) == "search_docs", "keep the @tool decorator and the 'search_docs' name"
_out = _asyncio.get_event_loop().run_until_complete(search_docs.handler({"query": "Pro plan API rate limit"}))
_txt = _out["content"][0]["text"]
assert isinstance(_txt, str) and _txt.strip(), "the tool should return the retrieved document text"
print("✓ TODO 6 complete — the agent now has a working tool it can choose to call.")
''',
        "teach": """\
An **agent** is an LLM in a loop with tools — *it* decides which tool to call and when. Your job is
to hand it good tools. The `@tool` decorator turns an ordinary async function into one the agent
can invoke; the **description** is how the model knows when to reach for it, so write it well.

### What to implement
Fill in the body of `search_docs(args)` (keep the `@tool(...)` decorator above it):
1. **Retrieve** for the agent's query: `hits = retrieve(args["query"], k=3)` — reusing the same
   RAG retriever from Form Factor 2.
2. **Format** the hits as a numbered string the model can cite:
   `text = "\\n".join(f"[{i+1}] {doc}" for i, (doc, _) in enumerate(hits))`.
3. **Return tool content** in the expected shape:
   `return {"content": [{"type": "text", "text": text}]}`.

> 💡 Notice you are *not* writing any `if`/`for` logic to decide when to search — the agent does
> that itself, based on your tool's description.""",
    },
    {
        "nb": "ff", "num": 7, "title": "Configure the autonomous builder",
        "locator": "builder_options = ClaudeAgentOptions(",
        "stub": '''builder_options = ClaudeAgentOptions()  # 🧩 TODO 7 — configure me. See docs/todo7.md
''',
        "check": '''# ✅ TODO 7 check — do not edit.
assert isinstance(builder_options, ClaudeAgentOptions), "builder_options must be a ClaudeAgentOptions"
assert builder_options.permission_mode == "bypassPermissions", \\
    "the builder runs unattended → permission_mode='bypassPermissions'"
assert {"Read", "Write", "Edit", "Bash"}.issubset(set(builder_options.allowed_tools or [])), \\
    "the builder needs Read, Write, Edit, and Bash to build & run code"
assert str(SANDBOX) in str(builder_options.cwd or ""), "keep the agent confined to the SANDBOX directory"
print("✓ TODO 7 complete — the autonomous builder is configured.")
''',
        "teach": """\
The top rung. The autonomous agent doesn't just *answer* — it **writes files and runs shell
commands** to build something, then fixes its own errors. That power needs guardrails, and those
guardrails live in `ClaudeAgentOptions`.

### What to implement
Replace the empty `ClaudeAgentOptions()` with a fully configured one:
- `model=MODEL`
- `cwd=str(SANDBOX)` — confine *all* file/shell ops to the sandbox directory.
- `allowed_tools=["Read", "Write", "Edit", "Bash"]` — the tools that let it build and run code.
- `permission_mode="bypassPermissions"` — autonomous: no human approval prompt per action.
- `max_turns=30` and `setting_sources=[]` — bound the loop; keep the run hermetic.
- `system_prompt="You are an automation engineer. Build the smallest correct solution, then
  verify it runs."`

> ⚠️ `bypassPermissions` + `Bash` means the agent executes code unattended. That's the whole point
> of this form factor — which is exactly why `cwd` pins it to a disposable sandbox.""",
    },
    # ───────────────────────── Evaluation notebook ─────────────────────────
    {
        "nb": "eval", "num": 8, "title": "Retrieval metrics — recall@k and MRR",
        "locator": "def hit_at_k(retrieved, relevant, k):",
        "stub": '''def hit_at_k(retrieved, relevant, k):
    # 🧩 TODO 8 — see docs/todo8.md
    raise NotImplementedError("Complete TODO 8 — open docs/todo8.md")


def mrr(retrieved, relevant):
    # 🧩 TODO 8 — see docs/todo8.md
    raise NotImplementedError("Complete TODO 8 — open docs/todo8.md")
''',
        "check": '''# ✅ TODO 8 check — do not edit.
assert hit_at_k(["a", "b", "c"], ["b"], 3) == 1.0, "a relevant doc IS in the top 3 → 1.0"
assert hit_at_k(["a", "b", "c"], ["b"], 1) == 0.0, "the relevant doc is NOT the top 1 → 0.0"
assert hit_at_k(["a"], ["z"], 3) == 0.0, "no relevant doc retrieved → 0.0"
assert abs(mrr(["x", "y", "z"], ["z"]) - (1 / 3)) < 1e-9, "first relevant doc is at rank 3 → 1/3"
assert mrr(["x", "y"], ["q"]) == 0.0, "no relevant doc → 0.0"
print("✓ TODO 8 complete — recall@k and MRR behave correctly.")
''',
        "teach": """\
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
> Part 1.1 are measuring under the hood.""",
    },
    {
        "nb": "eval", "num": 9, "title": "LLM-as-judge with structured output",
        "locator": "def claude_judge(rubric: str, material: str) -> dict:",
        "stub": '''def claude_judge(rubric: str, material: str) -> dict:
    # 🧩 TODO 9 — call Claude as an LLM judge, returning structured JSON. See docs/todo9.md
    raise NotImplementedError("Complete TODO 9 — open docs/todo9.md")
''',
        "check": '''# ✅ TODO 9 check — do not edit.
_v = correctness(
    {"question": "Pro rate limit?"},
    {"answer": "The Pro plan allows 1,000 requests per minute."},
    {"reference": "The Pro plan allows 1,000 requests per minute."},
)
assert set(_v) >= {"key", "score"}, "an evaluator returns at least {key, score}"
assert _v["score"] == 1.0, "an answer that matches the reference should score 1.0 for correctness"
print("✓ TODO 9 complete — your LLM judge grades open-ended answers:", _v)
''',
        "teach": """\
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
> grades are stable enough to compare experiments.""",
    },
    {
        "nb": "eval", "num": 10, "title": "Write LangSmith evaluators",
        "locator": "def category_match(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:",
        "stub": '''def category_match(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    # 🧩 TODO 10 — compare predicted vs. gold category. See docs/todo10.md
    raise NotImplementedError("Complete TODO 10 — open docs/todo10.md")


def urgency_match(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    # 🧩 TODO 10 — compare predicted vs. gold urgency. See docs/todo10.md
    raise NotImplementedError("Complete TODO 10 — open docs/todo10.md")
''',
        "check": '''# ✅ TODO 10 check — do not edit.
assert category_match({}, {"category": "billing"}, {"category": "billing"})["score"] == 1.0
assert category_match({}, {"category": "billing"}, {"category": "technical"})["score"] == 0.0
assert urgency_match({}, {"urgency": "high"}, {"urgency": "high"})["score"] == 1.0
_o = category_match({}, {"category": "billing"}, {"category": "billing"})
assert _o.get("key") == "category_match", "return a 'key' so LangSmith labels the metric"
print("✓ TODO 10 complete — your evaluators are ready to plug into ls.evaluate().")
''',
        "teach": """\
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
> for what it measures.""",
    },
]

# nb key -> (complete source notebook, student output notebook)
NB_FILES = {
    "ff": (WS / "ai_maturity_form_factors_complete.ipynb",
           WS / "ai_maturity_form_factors_student.ipynb"),
    "eval": (WS / "ai_maturity_form_factors_with_evaluation_complete.ipynb",
             WS / "ai_maturity_form_factors_with_evaluation_student.ipynb"),
}


def cell_md(text: str, cid: str) -> dict:
    return {"cell_type": "markdown", "id": cid, "metadata": {}, "source": text.splitlines(keepends=True)}


def cell_code(text: str, cid: str) -> dict:
    return {"cell_type": "code", "id": cid, "metadata": {}, "execution_count": None,
            "outputs": [], "source": text.splitlines(keepends=True)}


def write_doc(spec: dict, solution: str) -> None:
    img_md = ""
    if spec.get("img"):
        img_md = f'<img src="../images/{spec["img"]}" alt="{spec.get("img_alt", "")}" width="760">\n\n'
    body = (
        f"# 🧩 TODO {spec['num']} — {spec['title']}\n\n"
        f"{img_md}"
        f"{spec['teach']}\n\n"
        f"## ✅ Solution\n\n"
        f"Replace the placeholder cell with this, then run the **`✅ TODO {spec['num']} check`** cell:\n\n"
        f"```python\n{solution.rstrip()}\n```\n\n"
        f"_Generated from the complete notebook — this is the exact reference implementation._\n"
    )
    (DOCS / f"todo{spec['num']}.md").write_text(body, encoding="utf-8")


def build(nb_key: str) -> None:
    src_path, out = NB_FILES[nb_key]
    nb = json.loads(src_path.read_text(encoding="utf-8"))
    specs = [s for s in SPECS if s["nb"] == nb_key]

    new_cells: list[dict] = []
    matched = {s["num"]: 0 for s in specs}
    for cell in nb["cells"]:
        text = "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]
        spec = next((s for s in specs if cell["cell_type"] == "code" and s["locator"] in text), None)
        if spec is None:
            new_cells.append(cell)
            continue
        matched[spec["num"]] += 1
        write_doc(spec, text)  # the real cell source becomes the doc's solution
        new_cells.append(cell_md(POINTER.format(num=spec["num"], title=spec["title"]), f"todo{spec['num']}-md"))
        new_cells.append(cell_code(spec["stub"], f"todo{spec['num']}-blank"))
        new_cells.append(cell_code(spec["check"], f"todo{spec['num']}-check"))

    for num, count in matched.items():
        if count != 1:
            raise SystemExit(f"locator for TODO {num} matched {count} cells (expected exactly 1)")

    nb["cells"] = new_cells
    out.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{nb_key}: wrote {out.name}  (+{len(specs)} TODO docs)")


if __name__ == "__main__":
    for key in NB_FILES:
        build(key)
    print(f"docs in {DOCS}")
