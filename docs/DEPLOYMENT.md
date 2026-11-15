# Production Deployment Guide

This document outlines deployment options for running ViceWire in production.

---

## 1. Docker Deployment (Recommended)

### Using Docker Compose
The easiest way to run the service in production with automatic volume persistence and container restarts:

```bash
# Clone repository
git clone <your-repo-url>
cd <your-repo-name>

# Copy environment template
cp .env.example .env

# Build and start container in detached mode
docker compose up -d --build
```

### Checking Container Health
```bash
# Inspect container status
docker compose ps

# View live application logs
docker compose logs -f api
```

The database file will be persisted inside the named volume `vicewire_data` (`/app/data/gta_news.db`).

---

## 2. Bare-Metal / Systemd Deployment (Linux / Ubuntu)

### Step 1: Create Application Directory & Virtualenv
```bash
sudo mkdir -p /opt/vicewire
sudo chown $USER:$USER /opt/vicewire
cd /opt/vicewire

git clone <your-repo-url> .
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

### Step 2: Create Systemd Service Unit
Create `/etc/systemd/system/vicewire.service`:

```ini
[Unit]
Description=ViceWire GTA 6 & GTA Online API Service
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/vicewire
EnvironmentFile=/opt/vicewire/.env
ExecStart=/opt/vicewire/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable vicewire
sudo systemctl start vicewire
sudo systemctl status vicewire
```

---

## 3. Reverse Proxy Configuration (Nginx + SSL)

Install Nginx and Certbot:
```bash
sudo apt update && sudo apt install -y nginx certbot python3-certbot-nginx
```

Create `/etc/nginx/sites-available/vicewire`:
```nginx
server {
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_read_timeout 60s;
        proxy_connect_timeout 60s;
    }
}
```

Enable site and acquire free SSL certificate:
```bash
sudo ln -s /etc/nginx/sites-available/vicewire /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo certbot --nginx -d api.yourdomain.com
```

---

## 4. Production Environment Tuning

| Variable | Recommended Production Value | Description |
| :--- | :--- | :--- |
| `DEBUG` | `False` | Disables verbose debug logging and auto-reload |
| `PORT` | `8000` | Application bind port |
| `HOST` | `0.0.0.0` | Binds to all network interfaces |
| `DATABASE_PATH` | `/app/data/gta_news.db` | Absolute path in persistent storage |
| `POLL_INTERVAL_MINUTES` | `15` | Polling cadence for Rockstar Newswire checks |

