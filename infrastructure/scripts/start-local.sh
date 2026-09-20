#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
API_DIR="$ROOT/apps/api"
WEB_DIR="$ROOT/apps/web"
LOG_DIR="$ROOT/.run"
PATH="/opt/homebrew/opt/postgresql@16/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
export PATH

mkdir -p "$LOG_DIR"
test -f "$ROOT/.env" || cp "$ROOT/.env.example" "$ROOT/.env"

echo "Starting Postgres and Redis..."
brew services start postgresql@16 >/dev/null
brew services start redis >/dev/null

if ! curl -sf "http://127.0.0.1:8000/health" >/dev/null 2>&1; then
  echo "Starting API on http://127.0.0.1:8000 ..."
  (
    cd "$API_DIR"
    nohup .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload \
      >"$LOG_DIR/api.log" 2>&1 &
    echo $! >"$LOG_DIR/api.pid"
  )
else
  echo "API already running on port 8000."
fi

if ! curl -sf "http://127.0.0.1:3000" >/dev/null 2>&1; then
  echo "Starting web on http://127.0.0.1:3000 ..."
  (
    cd "$WEB_DIR"
    nohup npm run dev -- --hostname 127.0.0.1 --port 3000 \
      >"$LOG_DIR/web.log" 2>&1 &
    echo $! >"$LOG_DIR/web.pid"
  )
else
  echo "Web already running on port 3000."
fi

echo
echo "Jadon Family creatorOS & co. is starting."
echo "  App:     http://localhost:3000"
echo "  Public:  $ROOT/infrastructure/scripts/host-public.sh"
echo "  API:     http://localhost:8000/health"
echo "  Ready:   http://localhost:8000/health/ready"
echo "  Logs:    $LOG_DIR/"
echo
echo "Open the project in VS Code with:"
echo "  code $ROOT"
echo "Stop with: $ROOT/infrastructure/scripts/stop-local.sh"
