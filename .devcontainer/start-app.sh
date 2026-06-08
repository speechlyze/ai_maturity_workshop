#!/usr/bin/env bash
# Runs on every container start — auto-starts the app so the frontend loads.
cd "$(dirname "$0")/../app"

if pgrep -f "uvicorn backend.main:app" >/dev/null 2>&1; then
  echo "▸ App already running on port 8000."
  exit 0
fi

# Background uvicorn; the app retries the Oracle connection while the DB warms up.
nohup uvicorn backend.main:app --host 0.0.0.0 --port 8000 > /tmp/aiml-app.log 2>&1 &
echo "▸ App starting on port 8000 — the preview opens when it's ready (logs: /tmp/aiml-app.log)."
