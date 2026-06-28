#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# setup.sh - Configuracion del server privado como reverse proxy
# hacia los NodePorts del cluster K8s en la Cato
#
# Uso: sudo bash setup.sh
# Requiere: Debian/Ubuntu, acceso root, VPN activa al cluster
# ============================================================

NODE_IP="172.16.10.31"
WEBROOT="/var/www/certbot"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Paso 1: Instalar nginx y certbot ==="
apt update
apt install -y nginx certbot python3-certbot-nginx

echo "=== Paso 2: Configurar firewall ==="
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 32142/tcp

echo "=== Paso 3: Crear directorio webroot para certbot ==="
mkdir -p "$WEBROOT"

echo "=== Paso 4: Generar config temporal HTTP-only para obtener SSL ==="
cat > /etc/nginx/sites-available/peru <<TEMP_NGINX
server {
    listen 80;
    server_name peru.lidera.kr peruadmin.lidera.kr;

    location /.well-known/acme-challenge/ {
        root $WEBROOT;
    }

    location / {
        proxy_pass http://$NODE_IP:30007;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_buffering off;
        proxy_redirect off;
    }
}
TEMP_NGINX

ln -sf /etc/nginx/sites-available/peru /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo "=== Paso 5: Verificar e iniciar nginx ==="
nginx -t
systemctl start nginx
systemctl enable nginx

echo "=== Paso 6: Obtener certificados SSL con Let's Encrypt (modo --webroot) ==="
certbot certonly --webroot -w "$WEBROOT" \
    -d peru.lidera.kr \
    -d peruadmin.lidera.kr \
    --non-interactive \
    --agree-tos \
    --email admin@peru.lidera.kr \
    || certbot certonly --webroot -w "$WEBROOT" \
        -d peru.lidera.kr \
        -d peruadmin.lidera.kr

echo "=== Paso 7: Reemplazar config con la version final (con SSL) ==="
cp "$SCRIPT_DIR/nginx.conf" /etc/nginx/sites-available/peru
nginx -t
systemctl reload nginx

echo "=== Paso 8: Configurar renovacion automatica SSL ==="
echo "0 3 * * * root certbot renew --webroot -w $WEBROOT --quiet --post-hook 'systemctl reload nginx'" \
    > /etc/cron.d/certbot-renew

echo ""
echo "=== Listo! ==="
echo "Dominios configurados:"
echo "  https://peru.lidera.kr         -> $NODE_IP:30007 (Superior)"
echo "  https://peruadmin.lidera.kr    -> $NODE_IP:30006 (Admin)"
echo ""
echo "IMPORTANTE: Verifica que la VPN al cluster esta activa"
echo "  y que alcanzas $NODE_IP desde este servidor:"
echo "  curl -I http://$NODE_IP:30007"
