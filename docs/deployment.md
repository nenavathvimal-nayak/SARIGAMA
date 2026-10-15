# SARIGAMA Production Deployment Guide

## 1. Overview & System Requirements
SARIGAMA is designed for high-performance AI music generation. In production, it should be deployed on dedicated hardware with hardware acceleration:

- **Nvidia GPU**: CUDA 12.x, minimum 8GB VRAM (16GB+ recommended for LLM thinking mode).
- **Apple Silicon**: M1/M2/M3/M4 with unified memory (Metal / MLX).
- **AMD GPU**: ROCm 6.x (Linux).
- **Intel GPU**: Intel oneAPI / XPU.
- **System Memory**: 16GB+ RAM minimum.
- **Storage**: Fast NVMe SSD for model weights and audio scratch directories.

---

## 2. Environment Configuration

Create a production `.env` file from `.env.example`:

```bash
cp .env.example .env
chmod 600 .env
```

### Essential Production Variables
```ini
# Declare production mode (enforces strict auth and fail-closed security)
SARIGAMA_ENV=production

# High-entropy API key for all protected routes
SARIGAMA_API_KEY=your-32-char-random-secret-key-here

# Upload size limit (default 50MB)
SARIGAMA_MAX_UPLOAD_SIZE_MB=50

# CORS Whitelist (comma-separated allowed origins)
SARIGAMA_CORS_ORIGINS=https://app.yourdomain.com

# Queue and Worker Configuration (keep 1 worker per GPU)
ACESTEP_QUEUE_MAXSIZE=200
ACESTEP_QUEUE_WORKERS=1

# Storage directory for checkpoints
ACESTEP_CHECKPOINTS_DIR=/opt/sarigama/models
```

---

## 3. Reverse Proxy Architecture (Recommended)

In production, run SARIGAMA bound to `127.0.0.1:8000` and use Nginx or Caddy to terminate TLS, enforce rate limits, and proxy requests.

### Sample Nginx Configuration
```nginx
# Rate limiting zone: 10 requests/sec with burst of 20
limit_req_zone $binary_remote_addr zone=sarigama_limit:10m rate=10r/s;

server {
    listen 443 ssl http2;
    server_name api.sarigama.example.com;

    ssl_certificate /etc/letsencrypt/live/api.sarigama.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.sarigama.example.com/privkey.pem;

    # Maximum payload size (align with SARIGAMA_MAX_UPLOAD_SIZE_MB)
    client_max_body_size 60M;

    # Timeouts for long-running generation queries
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;

    location / {
        limit_req zone=sarigama_limit burst=20 nodelay;

        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Public unauthenticated health check
    location = /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

---

## 4. Systemd Service Setup (Linux)

Create `/etc/systemd/system/sarigama.service`:

```ini
[Unit]
Description=SARIGAMA AI Music API Service
After=network.target

[Service]
Type=simple
User=sarigama
Group=sarigama
WorkingDirectory=/opt/sarigama
EnvironmentFile=/opt/sarigama/.env
ExecStart=/opt/sarigama/.venv/bin/python acestep/api_server.py --port 8000
Restart=always
RestartSec=5
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now sarigama
```

---

## 5. Health Checks & Monitoring

SARIGAMA exposes two primary monitoring endpoints:

1. **Service Readiness / Health**:
   ```bash
   curl -s http://127.0.0.1:8000/health
   ```
   *Response*:
   ```json
   {
     "status": "ok",
     "service": "SARIGAMA API",
     "version": "1.0",
     "models_initialized": true,
     "llm_initialized": true,
     "loaded_model": "acestep-v15-turbo"
   }
   ```

2. **Job Queue & Server Statistics** (Protected by `SARIGAMA_API_KEY`):
   ```bash
   curl -s -H "Authorization: Bearer <API_KEY>" http://127.0.0.1:8000/v1/stats
   ```
   *Response*:
   ```json
   {
     "jobs": {
       "total": 12,
       "queued": 1,
       "running": 1,
       "succeeded": 10,
       "failed": 0
     },
     "queue_size": 1,
     "queue_maxsize": 200,
     "avg_job_seconds": 4.8
   }
   ```
