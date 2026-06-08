#!/usr/bin/env bash
# Runs once when the Codespace / dev container is created.
set -euo pipefail

echo "▸ Installing app dependencies…"
python -m pip install --upgrade pip
python -m pip install -r app/requirements.txt

echo "▸ Installing notebook tooling…"
python -m pip install jupyterlab ipykernel langsmith

echo "▸ Installing the Claude Agent CLI (Form Factors 4 & 5)…"
npm install -g @anthropic-ai/claude-code || echo "  (skipped — the agent pages will show an install hint)"

echo "▸ Building the Oracle schema + warming the embedding model…"
# store.initialize() connects to Oracle (retrying while it warms up), creates the
# acme_docs table + vector/text indexes, ingests the docs, and downloads the
# fastembed model — so the database and the app are ready the moment you arrive.
( cd app && python -c "from backend.core.retrieval import store; store.initialize(); print('  retrieval backend:', store.status())" ) \
  || echo "  (Oracle not ready yet — the app will build the schema on first run)"

cat <<'EOF'

✓ Setup complete — the app auto-starts on port 8000 (preview opens automatically).
  • Restart it manually:  cd app && ./run.sh
  • App logs:             /tmp/aiml-app.log
  • Notebooks:            open any .ipynb, choose the Python 3.12 kernel
EOF
