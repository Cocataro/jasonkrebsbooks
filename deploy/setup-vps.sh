#!/usr/bin/env bash
# One-time VPS setup for jasonkrebsbooks.com
# Run this ON THE VPS (via Tailscale SSH) as root or with sudo.
#
# Usage (on the VPS):
#   curl -sSL https://raw.githubusercontent.com/Cocataro/jasonkrebsbooks/main/deploy/setup-vps.sh | sudo bash
# OR:
#   sudo bash setup-vps.sh
#
# What this does:
#   1. Installs nginx + certbot if missing
#   2. Creates /var/www/jasonkrebsbooks directory
#   3. Drops a placeholder index.html so you can verify DNS before full deploy
#   4. Configures nginx for jasonkrebsbooks.com + www.jasonkrebsbooks.com
#   5. Prints TLS setup command (run AFTER DNS has propagated)

set -euo pipefail

DOMAIN="jasonkrebsbooks.com"
WEBROOT="/var/www/jasonkrebsbooks"

echo "==> Detecting OS"
if command -v apt-get >/dev/null 2>&1; then
    PKG="apt-get"
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq
elif command -v dnf >/dev/null 2>&1; then
    PKG="dnf"
elif command -v yum >/dev/null 2>&1; then
    PKG="yum"
else
    echo "Unsupported package manager. Install nginx + certbot manually." >&2
    exit 1
fi

echo "==> Installing nginx and certbot"
if [ "$PKG" = "apt-get" ]; then
    apt-get install -y nginx certbot python3-certbot-nginx rsync
else
    $PKG install -y nginx certbot python3-certbot-nginx rsync
fi

echo "==> Creating web root"
mkdir -p "$WEBROOT"
chown -R www-data:www-data "$WEBROOT" 2>/dev/null || chown -R nginx:nginx "$WEBROOT" 2>/dev/null || true
chmod -R 755 "$WEBROOT"

echo "==> Writing placeholder index.html"
cat > "$WEBROOT/index.html" <<'EOF'
<!DOCTYPE html>
<html><head><title>jasonkrebsbooks.com — coming soon</title></head>
<body style="font-family:serif;text-align:center;padding:3rem;background:#faf6ef;color:#2a2017">
<h1>The Crossroads Inn</h1>
<p>A cozy fantasy series — coming soon.</p>
<p style="opacity:0.6;font-size:0.9rem">Site deployment in progress.</p>
</body></html>
EOF

echo "==> Writing nginx site config"
cat > /etc/nginx/sites-available/jasonkrebsbooks <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;

    root $WEBROOT;
    index index.html;

    # Security-ish headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Gzip for text assets
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json image/svg+xml;

    # Long cache for hashed assets (Astro generates hashed filenames)
    location ~* ^/_astro/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # RSS and sitemap - short cache
    location = /rss.xml {
        expires 1h;
    }
    location = /sitemap-index.xml {
        expires 1h;
    }

    # Astro generates directory-style routes (e.g. /about/index.html)
    # Try file first, then dir with index.html, then 404
    location / {
        try_files \$uri \$uri/ \$uri/index.html \$uri.html =404;
    }

    # Clean URL redirects for branded short links (handled by Astro-generated HTML
    # meta-refresh pages — /news, /follow, /review are real pages in the site)
}
EOF

# Enable site
if [ ! -L /etc/nginx/sites-enabled/jasonkrebsbooks ]; then
    ln -s /etc/nginx/sites-available/jasonkrebsbooks /etc/nginx/sites-enabled/jasonkrebsbooks
fi

# Remove default nginx site if it's in the way
if [ -f /etc/nginx/sites-enabled/default ]; then
    echo "==> Removing default nginx site"
    rm /etc/nginx/sites-enabled/default
fi

echo "==> Testing nginx config"
nginx -t

echo "==> Reloading nginx"
systemctl reload nginx
systemctl enable nginx

echo ""
echo "=========================================="
echo "VPS setup complete."
echo "=========================================="
echo ""
echo "NEXT STEPS (in this order):"
echo ""
echo "1. Set DNS A records in Hostinger:"
echo "     jasonkrebsbooks.com       A   <your VPS IP>"
echo "     www.jasonkrebsbooks.com   A   <your VPS IP>"
echo ""
echo "2. Wait 5-10 minutes for DNS to propagate. Verify:"
echo "     dig jasonkrebsbooks.com +short"
echo "   Should return your VPS IP."
echo ""
echo "3. Once DNS is live, request TLS cert:"
echo "     sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo "   Accept the prompts. certbot will update the nginx config with HTTPS."
echo ""
echo "4. Run the deploy script from your Mac:"
echo "     ./deploy/deploy.sh"
echo ""
echo "Placeholder page live now at:  http://$DOMAIN  (once DNS propagates)"
