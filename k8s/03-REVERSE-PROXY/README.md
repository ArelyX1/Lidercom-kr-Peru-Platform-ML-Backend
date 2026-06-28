# 03-REVERSE-PROXY — Servidor Privado (Reverse Proxy)

## Arquitectura

```
[Usuario] → Cafe24 DNS → 200.234.225.16 (server privado)
                                │ nginx + SSL
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
      172.16.10.31:30005   :30006           :30007
      (backend API)    (admin frontend) (superior frontend)
```

## Setup paso a paso (manual)

### 1. Requisitos
- VPN activa hacia el cluster (debe alcanzar `172.16.10.31`)
- DNS Cafe24 apuntando:
  - `peru.lidera.kr` → `200.234.225.16`
  - `peruadmin.lidera.kr` → `200.234.225.16`

### 2. Verificar VPN y acceso a NodePorts
```bash
curl -I http://172.16.10.31:30007  # superior frontend
curl -I http://172.16.10.31:30006  # admin frontend
curl -I http://172.16.10.31:30005  # backend
```

### 3. Instalar nginx + certbot
```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
```

### 4. Firewall: abrir puertos
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 32142/tcp
```

### 5. Crear webroot para certbot
```bash
sudo mkdir -p /var/www/certbot
```

### 6. Config nginx TEMPORAL (solo HTTP, sin SSL)
Crear `/etc/nginx/sites-available/peru` con este contenido:

```nginx
server {
    listen 80;
    server_name peru.lidera.kr peruadmin.lidera.kr;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://172.16.10.31:30007;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_redirect off;
    }
}
```

### 7. Activar sitio y arrancar nginx
```bash
sudo ln -sf /etc/nginx/sites-available/peru /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 8. Obtener certificados SSL (Let's Encrypt)
```bash
sudo certbot certonly --webroot -w /var/www/certbot \
    -d peru.lidera.kr \
    -d peruadmin.lidera.kr
```
Esto crea los archivos en `/etc/letsencrypt/live/peru.lidera.kr/`.

### 9. Aplicar config FINAL con SSL
Reemplazar `/etc/nginx/sites-available/peru` con el contenido de `nginx.conf`
(de este directorio), luego:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 10. Verificar
```bash
curl -I https://peru.lidera.kr
curl -I https://peruadmin.lidera.kr
```

### 11. Renovacion automatica SSL
```bash
echo "0 3 * * * root certbot renew --webroot -w /var/www/certbot --quiet --post-hook 'systemctl reload nginx'" \
    | sudo tee /etc/cron.d/certbot-renew
```

## Archivos en este directorio

| Archivo | Descripcion |
|---|---|
| `nginx.conf` | Config final con SSL (usar en paso 9) |
| `setup.sh` | Version automatizada de todos los pasos |

## Notas

- El server privado NO almacena datos de la aplicacion
- El frontend nginx interno (dentro del pod) proxea `/graphql` a `172.16.10.31:30005`
- Cloudflare Tunnel sigue activo para `admin.neravy.us` y `lidercom.neravy.us`
