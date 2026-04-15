#!/usr/bin/env bash
# Deploy jasonkrebsbooks.com to the Hostinger VPS over Tailscale SSH.
# Run from your Mac inside the project directory.
#
# Usage:
#   ./deploy/deploy.sh
#
# Prerequisites:
#   - Tailscale connected to the VPS
#   - SSH access working: ssh <user>@<vps-tailscale-name>
#   - setup-vps.sh has been run ONCE on the VPS
#   - DNS A records point to VPS IP
#   - TLS cert installed via certbot
#
# Configure the VPS target by editing the variables below, or setting
# them in your shell environment before running this script.

set -euo pipefail

# --------- EDIT THESE OR SET AS ENV VARS ---------
# Your Tailscale hostname or IP for the VPS (replace with the actual one)
VPS_HOST="${VPS_HOST:-srv1377312}"     # Tailscale device name, or "<user>@<tailscale-ip>"
VPS_USER="${VPS_USER:-root}"           # SSH user
WEBROOT="${WEBROOT:-/var/www/jasonkrebsbooks}"
# -------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "==> Building site locally"
if ! command -v npm >/dev/null 2>&1; then
    echo "npm not found. Install Node.js 20+: https://nodejs.org" >&2
    exit 1
fi

if [ ! -d node_modules ]; then
    echo "==> Installing dependencies (first run)"
    npm install
fi

npm run build

if [ ! -d dist ]; then
    echo "Build failed — no dist/ directory produced." >&2
    exit 1
fi

echo ""
echo "==> Syncing to VPS ($VPS_USER@$VPS_HOST:$WEBROOT)"
if ! command -v rsync >/dev/null 2>&1; then
    echo "rsync not found. Install: brew install rsync" >&2
    exit 1
fi

# Rsync the built site up; --delete removes stale files no longer in the build
rsync -avz --delete \
    --exclude ".DS_Store" \
    --exclude ".git" \
    dist/ "$VPS_USER@$VPS_HOST:$WEBROOT/"

echo ""
echo "==> Done"
echo ""
echo "Live at:  https://jasonkrebsbooks.com"
echo ""
echo "If the site doesn't update, verify on VPS:"
echo "  ssh $VPS_USER@$VPS_HOST 'ls -la $WEBROOT'"
