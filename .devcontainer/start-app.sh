#!/usr/bin/env bash
# Runs on every container start — auto-starts the app so the frontend loads.
cd "$(dirname "$0")/../app" || exit 0

# Already up? (curl the health endpoint — more reliable than matching the process.)
if curl -sf -o /dev/null http://127.0.0.1:8000/api/health 2>/dev/null; then
  echo "▸ App already running on port 8000."
  exit 0
fi

# Launch fully detached so the server survives this lifecycle hook exiting (a plain
# `&` gets reaped). setsid (a new session) is the strongest detachment and ships on
# the Linux dev-container image; fall back to nohup+disown where it's absent (macOS).
# `python -m uvicorn` avoids depending on the console script being on PATH.
if command -v setsid >/dev/null 2>&1; then
  setsid nohup python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 </dev/null >/tmp/aiml-app.log 2>&1 &
else
  nohup python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 </dev/null >/tmp/aiml-app.log 2>&1 &
fi
disown 2>/dev/null || true

# Wait for it to bind so any startup crash shows up in the creation log.
for _ in $(seq 1 20); do
  sleep 1
  if curl -sf -o /dev/null http://127.0.0.1:8000/api/health 2>/dev/null; then
    echo "✓ App is up on port 8000 — the preview will open."
    exit 0
  fi
done

echo "⚠ App did not bind to port 8000 within 20s. Last log lines:"
tail -n 30 /tmp/aiml-app.log 2>/dev/null || true
exit 0   # never fail the lifecycle hook
