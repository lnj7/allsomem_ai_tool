#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG_DIR="$ROOT/.run"
PATH="/opt/homebrew/opt/postgresql@16/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
export PATH

mkdir -p "$LOG_DIR"

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "Installing Cloudflare Tunnel..."
  brew install cloudflared
fi

"$ROOT/infrastructure/scripts/start-local.sh"

echo
echo "Publishing a public HTTPS URL (this Mac must stay awake and online)..."
echo "Reviewers open the trycloudflare.com link. Stop with Ctrl+C or stop-local.sh plus killing cloudflared."
echo

cloudflared tunnel --url http://127.0.0.1:3000 --no-autoupdate
