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

cat <<'EOF'

✓ Setup complete.
  • Start the app:  cd app && ./run.sh        (→ forwarded on port 8000)
  • Notebooks:      open any .ipynb, choose the Python 3.12 kernel
  • RAG runs on the in-memory backend here (ORACLE_ENABLED=0). To use Oracle,
    set ORACLE_ENABLED=1 and point ORACLE_DSN at a reachable database.
EOF
