#!/usr/bin/env bash
# One-time VPS setup for jasonkrebsbooks.com on the Hostinger VPS.
# Assumes Traefik + Docker are already running (same pattern as Paperclip).
#
# Run ONCE on the VPS (root):
#   curl -sSL https://raw.githubusercontent.com/Cocataro/jasonkrebsbooks/main/deploy/setup-vps.sh | sudo bash

set -euo pipefail

DEPLOY_DIR="/docker/jasonkrebsbooks"
REPO_RAW="https://raw.githubusercontent.com/Cocataro/jasonkrebsbooks/main/deploy"

echo "==> Verifying prerequisites"
if ! command -v docker >/dev/null 2>&1; then
    echo "Docker not found. This VPS should already have it (Traefik is running there)." >&2
    exit 1
fi
if ! docker ps --format '{{.Names}}' | grep -q 'traefik'; then
    echo "Traefik container not running. Expected 'traefik-traefik-1' or similar." >&2
    exit 1
fi

echo "==> Stopping + disabling any host nginx (Traefik owns ports 80/443)"
if systemctl is-enabled nginx >/dev/null 2>&1; then
    systemctl disable nginx || true
fi
if systemctl is-active nginx >/dev/null 2>&1; then
    systemctl stop nginx || true
fi
# Drop the sites-enabled stub we created earlier (if present)
rm -f /etc/nginx/sites-enabled/jasonkrebsbooks

echo "==> Creating deploy directory at $DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR/site"

echo "==> Downloading docker-compose.yml + nginx-site.conf"
curl -sSL "$REPO_RAW/docker-compose.yml" -o "$DEPLOY_DIR/docker-compose.yml"
curl -sSL "$REPO_RAW/nginx-site.conf" -o "$DEPLOY_DIR/nginx-site.conf"

echo "==> Writing placeholder index.html"
cat > "$DEPLOY_DIR/site/index.html" <<'EOF'
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>jasonkrebsbooks.com — coming soon</title></head>
<body style="font-family:Georgia,serif;text-align:center;padding:3rem;background:#faf6ef;color:#2a2017;max-width:40rem;margin:auto">
<h1 style="font-size:2.5rem">The Crossroads Inn</h1>
<p style="font-size:1.2rem;color:#4e4236">A cozy fantasy series — coming soon.</p>
<p style="opacity:0.6;font-size:0.9rem;margin-top:3rem">Site deployment in progress.</p>
</body></html>
EOF

echo "==> Starting site container"
cd "$DEPLOY_DIR"
docker compose up -d

sleep 2
docker compose ps

echo ""
echo "=========================================="
echo "VPS setup complete."
echo "=========================================="
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Set DNS A records in Hostinger → Domains → jasonkrebsbooks.com → DNS:"
echo "     jasonkrebsbooks.com       A   187.77.31.153"
echo "     www.jasonkrebsbooks.com   A   187.77.31.153"
echo ""
echo "2. Wait 5-10 minutes. Verify:"
echo "     dig jasonkrebsbooks.com +short"
echo "   Traefik auto-provisions TLS via Let's Encrypt once DNS resolves."
echo ""
echo "3. Deploy the real site from your Mac:"
echo "     cd /path/to/jasonkrebsbooks-site && ./deploy/deploy.sh"
echo ""
echo "Logs:"
echo "  Site container: docker logs -f jasonkrebsbooks-site"
echo "  Traefik:        docker logs -f traefik-traefik-1"
