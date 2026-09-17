#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG_DIR="$ROOT/.run"

stop_pidfile() {
  local file="$1"
  if [[ -f "$file" ]]; then
    local pid
    pid="$(cat "$file")"
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
    rm -f "$file"
  fi
}

stop_pidfile "$LOG_DIR/api.pid"
stop_pidfile "$LOG_DIR/web.pid"

# Also stop leftover processes on the app ports.
for port in 8000 3000; do
  pids="$(lsof -tiTCP:$port -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "$pids" ]]; then
    kill $pids 2>/dev/null || true
  fi
done

echo "CreatorOS API and web stopped."
echo "Postgres and Redis were left running. Stop them with:"
echo "  brew services stop postgresql@16"
echo "  brew services stop redis"
