# The AI Maturity Ladder

Climb from a plain LLM chatbot to an autonomous agent that writes and runs its own code — **one rung at a time**. A hands-on workshop (notebooks) plus a polished web app, built around a single running example: a support assistant for the fictional **Acme Cloud**, implemented five ways.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/AscXend/ai_maturity_workshop?quickstart=1)

---

## Quick start

### In GitHub Codespaces (zero local setup)
1. Click **Open in GitHub Codespaces** above (or **Code ▸ Codespaces ▸ Create**).
2. When prompted, set the **`ANTHROPIC_API_KEY`** secret (and optionally `LANGSMITH_API_KEY` for the evaluation notebook). The dev container installs everything on create.
3. Run the app: `cd app && ./run.sh` → open the forwarded **port 8000**.
4. Or open any `.ipynb` and pick the **Python 3.12** kernel.

RAG uses an in-memory vector index in Codespaces (`ORACLE_ENABLED=0`); set it to `1` with a reachable `ORACLE_DSN` to use Oracle AI Database.

### Locally
```bash
cd app && ./run.sh          # uses the `dbtlabs` conda env if present → http://127.0.0.1:8000
```
See [`app/README.md`](app/README.md) for full app details.

---

## 📓 Notebooks

The workshop ships **complete** notebooks (the reference) and **student** notebooks (fill-in-the-blank). In a student notebook, key cells are replaced with a placeholder; a markdown cell links to a guided **TODO doc** in [`docs/`](docs/), and an `assert` cell gates progress until your code is correct.

| Notebook | Variant | What it teaches | TODOs |
|---|---|---|---|
| [`ai_maturity_form_factors.ipynb`](ai_maturity_form_factors.ipynb) | ✅ Complete | The five form factors: chatbot → RAG → workflow → agent → autonomous agent. Oracle-backed RAG (vector / keyword / hybrid / graph + quantization), `claude-agent-sdk` for FF4–5. | — |
| [`ai_maturity_form_factors_student.ipynb`](ai_maturity_form_factors_student.ipynb) | ✏️ Student | Same, with 7 cells to complete | [1](docs/todo1.md)–[7](docs/todo7.md) |
| [`ai_maturity_form_factors_with_evaluation.ipynb`](ai_maturity_form_factors_with_evaluation.ipynb) | ✅ Complete | Evaluating the ladder with **LangSmith**: retrieval metrics (recall@k, MRR), LLM-as-judge (correctness & groundedness), classifier accuracy. | — |
| [`ai_maturity_form_factors_with_evaluation_student.ipynb`](ai_maturity_form_factors_with_evaluation_student.ipynb) | ✏️ Student | Same, with 3 cells to complete | [8](docs/todo8.md)–[10](docs/todo10.md) |

**How a student works through it:** run cells top to bottom → hit a 🧩 **TODO** markdown cell → open the linked `docs/todoN.md` → read the explanation → paste the solution snippet into the placeholder cell → run the ✅ **check** cell (it must pass) → continue.

### TODO map

| TODO | Notebook | Concept |
|---|---|---|
| [1](docs/todo1.md) | Form factors | Multi-turn memory (`Chatbot.send`) |
| [2](docs/todo2.md) | Form factors | Oracle vector search (`VECTOR_DISTANCE`) |
| [3](docs/todo3.md) | Form factors | Grounded, cited RAG answer |
| [4](docs/todo4.md) | Form factors | Structured output classification |
| [5](docs/todo5.md) | Form factors | Orchestrating the workflow pipeline |
| [6](docs/todo6.md) | Form factors | Giving an agent a tool (`@tool`) |
| [7](docs/todo7.md) | Form factors | Configuring the autonomous builder |
| [8](docs/todo8.md) | Evaluation | Retrieval metrics: recall@k & MRR |
| [9](docs/todo9.md) | Evaluation | LLM-as-judge with structured output |
| [10](docs/todo10.md) | Evaluation | Writing LangSmith evaluators |

---

## 🖥️ The app

A FastAPI + vanilla-JS app (sleek, light/dark) that turns the five form factors into an interactive UI — the sidebar is a literal ladder. Everything streams over SSE.

| # | Page | Form factor | What it shows |
|---|---|---|---|
| 1 | LLM Chatbot | The Chatbot | Multi-turn chat; "memory" = the growing message list re-sent each turn |
| 2 | RAG Chatbot | Retrieval-Augmented Generation | Vector / keyword / hybrid retrieval + a grounded, cited answer (Oracle, or in-memory fallback) |
| 3 | LLM Workflow | The LLM-Driven Workflow | classify → route → retrieve → draft → review/revise, streamed stage by stage |
| 4 | Autonomous Agent | The Agent | Tool-using agent (`search_docs`, `create_support_ticket`); the model picks the path |
| 5 | Agent That Builds | The Autonomous Agent | Writes a script, runs it, fixes its own errors in a sandbox; inspect the artifacts |

Details, architecture, and the graceful-degradation notes are in [`app/README.md`](app/README.md).

---

## Requirements

- **`ANTHROPIC_API_KEY`** — required everywhere (model defaults to `claude-opus-4-8`). In Codespaces, set it as a secret; locally, put it in a `.env`.
- **Oracle AI Database** — optional for the app (in-memory fallback); the notebooks' RAG section expects it.
- **Claude Agent SDK + `claude` CLI** — for Form Factors 4 & 5 (the dev container installs it).
- **`LANGSMITH_API_KEY`** — only for the evaluation notebook.

## Layout

```
ai_maturity_workshop/
├── .devcontainer/                 Codespaces / dev-container setup
├── ai_maturity_form_factors*.ipynb            complete + _student
├── ai_maturity_form_factors_with_evaluation*.ipynb
├── docs/                          todo1.md … todo10.md (guided fill-ins)
├── scripts/                       student-notebook generator
└── app/                           FastAPI backend + JS frontend
```
