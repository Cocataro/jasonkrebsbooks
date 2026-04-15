#!/usr/bin/env bash
# Deploy jasonkrebsbooks.com to the Hostinger VPS over Tailscale SSH.
# Builds Astro locally, rsyncs dist/ into the Docker-mounted volume.
# Run from your Mac inside the project directory.

set -euo pipefail

VPS_HOST="${VPS_HOST:-100.117.71.125}"
VPS_USER="${VPS_USER:-root}"
VPS_SITE_DIR="${VPS_SITE_DIR:-/docker/jasonkrebsbooks/site}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "==> Building site"
if [ ! -d node_modules ]; then
    echo "==> Installing dependencies (first run)"
    npm install
fi
npm run build

if [ ! -d dist ]; then
    echo "Build failed — no dist/ produced." >&2
    exit 1
fi

echo ""
echo "==> Syncing dist/ to VPS ($VPS_USER@$VPS_HOST:$VPS_SITE_DIR)"
rsync -avz --delete \
    --exclude ".DS_Store" \
    dist/ "$VPS_USER@$VPS_HOST:$VPS_SITE_DIR/"

echo ""
echo "==> Done. Live at https://jasonkrebsbooks.com"
