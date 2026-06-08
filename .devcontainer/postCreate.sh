#!/usr/bin/env bash
# Runs once when the Codespace / dev container is created.
set -euo pipefail

echo "▸ Installing app dependencies…"
python -m pip install --upgrade pip
python -m pip install -r app/requirements.txt

echo "▸ Installing notebook tooling…"
# `datasets` is needed by Part 4 of the evaluation notebook (the BEIR benchmark)
# and by scripts/seed_beir.py below.
python -m pip install jupyterlab ipykernel langsmith datasets

echo "▸ Installing the Claude Agent CLI (Form Factors 4 & 5)…"
npm install -g @anthropic-ai/claude-code || echo "  (skipped — the agent pages will show an install hint)"

echo "▸ Building the Oracle schema + warming the embedding model…"
# store.initialize() connects to Oracle (retrying while it warms up), creates the
# acme_docs table + vector/text indexes, ingests the docs, and downloads the
# fastembed model — so the database and the app are ready the moment you arrive.
( cd app && python -c "from backend.core.retrieval import store; store.initialize(); print('  retrieval backend:', store.status())" ) \
  || echo "  (Oracle not ready yet — the app will build the schema on first run)"

echo "▸ Seeding the autonomous-builder sample dataset…"
( cd app && python -c "from backend.core.sandbox import reset_sandbox; reset_sandbox(); print('  sandbox seeded with support_messages.csv')" )

echo "▸ Pre-seeding the BEIR scifact benchmark (corpus + embeddings) for the evaluation notebook…"
# Embedding ~2,000 abstracts is the slow step of the evaluation notebook's Part 4.
# Do it once here (idempotent) so it persists in the oracle-data volume and the
# notebook skips straight to evaluation. Safe to skip if Oracle isn't up yet.
python scripts/seed_beir.py \
  || echo "  (BEIR seed skipped — the evaluation notebook will build it on first run)"

cat <<'EOF'

✓ Setup complete — the app auto-starts on port 8000 (preview opens automatically).
  • Restart it manually:  cd app && ./run.sh
  • App logs:             /tmp/aiml-app.log
  • Notebooks:            open any .ipynb, choose the Python 3.12 kernel
EOF
