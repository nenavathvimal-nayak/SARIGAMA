# DHAAVLO MUSICAL INTELLIGENCE (DHAVLO MI) Security Architecture & Policy

## 1. Overview & Security Mission
DHAAVLO MUSICAL INTELLIGENCE (DHAVLO MI) is an AI-powered music intelligence and generation platform built on diffusion transformer (DiT) architectures and language models. The generation pipeline is compute- and memory-intensive; therefore, application security focuses on protecting model runtimes, preventing resource exhaustion (Denial of Service), restricting arbitrary filesystem access, and securing API endpoints.

---

## 2. Threat Model & Trust Boundaries

```
[ External Client / Web UI ]
             │ (HTTPS)
             ▼
[ Reverse Proxy (Nginx/Caddy) ]  --> TLS Termination, Rate Limiting, IP Filtering
             │ (HTTP localhost:8000)
             ▼
[ DHAVLO MI FastAPI Application ]
  ├── Auth Verification (timing-safe, fail-closed in production)
  ├── Request Validation (Pydantic bounded schemas)
  ├── File Security (extension whitelist, path traversal check, size limits)
  └── Job Queue (bounded in-memory queue, single GPU worker)
             │
             ▼
[ Model Runtime (PyTorch / MLX / CUDA) ]
```

### Trust Zones
1. **Public Zone**: Untrusted clients calling the API over the network.
2. **Proxy Zone**: Reverse proxy providing TLS termination and front-line rate limiting.
3. **Application Zone**: Python FastAPI service running in dedicated virtual environment or container.
4. **Hardware Runtime**: Direct access to GPU/MPS unified memory and model weights.

---

## 3. Authentication & Authorization

### Supported Authentication Methods
Protected endpoints require authentication using a shared API key:
- **Authorization Header**: `Authorization: Bearer <DHAVLO_MI_API_KEY>` (or `SARIGAMA_API_KEY`)
- **Request Body (Legacy Compatible)**: `{"ai_token": "<DHAVLO_MI_API_KEY>", ...}`

### Timing-Safe Token Verification
All token comparisons use constant-time digest verification (`secrets.compare_digest`) to prevent timing side-channel attacks.

### Fail-Closed in Production
- When `DHAVLO_MI_ENV=production` (or `SARIGAMA_ENV=production`), leaving `DHAVLO_MI_API_KEY` unset causes the application to **fail closed**: all protected endpoint requests immediately return `HTTP 500 Authentication misconfigured`.
- In local development (`DHAVLO_MI_ENV=development` or empty), omitting the API key allows open local testing.

### User Identity & Multi-Tenancy Boundary
DHAVLO MI currently operates as a dedicated, single-tenant or shared-secret service. Job records are ephemeral and identified by cryptographically random UUIDv4 identifiers.
> **Roadmap Note**: For public multi-user deployments, an external authentication layer (e.g., OAuth2, JWT with user IDs) should be placed in front of the service, binding job records to specific user identities.

---

## 4. File Uploads & Path Security

### Audio Extension Whitelist
Audio inputs are strictly validated against approved audio formats:
- `.wav`, `.mp3`, `.flac`, `.ogg`, `.m4a`, `.aac`, `.opus`, `.wma`
- Arbitrary extensions (e.g., `.py`, `.sh`, `.exe`, `.json`) are rejected with `HTTP 400`.

### Path Traversal Defense
- **Absolute Paths**: Restricted exclusively to the designated system temporary directory.
- **Relative Paths**: Inspected for traversal sequences (`..`). Paths containing traversal markers or hidden files (`.env`, `.git`) are rejected with `HTTP 400`.
- **Generated Audio Retrieval (`/v1/audio`)**: Constrained strictly within `app.state.temp_audio_dir`. Non-audio extensions and paths outside the directory return `HTTP 403` or `HTTP 400`.

### Upload Size & Disk Protection
- Upload streaming enforces a configurable byte ceiling (default: `50MB`, controlled via `DHAVLO_MI_MAX_UPLOAD_SIZE_MB` with fallback to `SARIGAMA_MAX_UPLOAD_SIZE_MB`).
- Exceeding the size limit halts streaming, removes partial files immediately, and returns `HTTP 413 Payload Too Large`.
- All temporary upload files are cleaned up on error or after job completion.

---

## 5. API Input Validation & Resource Quotas

To prevent memory bloat, GPU out-of-memory (OOM) crashes, and resource starvation, all API inputs are bounded via Pydantic schemas:

| Field | Range / Limit | Default | Purpose |
|---|---|---|---|
| `prompt` | Max 4,096 chars | `""` | Prevents token buffer exhaustion |
| `global_caption` | Max 4,096 chars | `""` | Full-song description ceiling |
| `lyrics` | Max 32,768 chars | `""` | Prevents megabyte lyric payloads |
| `inference_steps` | 1 to 200 | 8 | Prevents GPU compute lockups |
| `batch_size` | 1 to 8 | 1 | Prevents GPU VRAM OOM crashes |
| `audio_duration` | -1.0 to 600.0s | None | Caps generated audio at 10 minutes |
| `bpm` | 20 to 300 | None | Bounds musical tempo parameters |
| `guidance_scale` | 0.0 to 50.0 | 7.0 | Bounds diffusion guidance |
| `audio_code_string` | Max 65,536 chars | `""` | Bounds semantic code strings |

---

## 6. Job Queue & Overload Protection

- **Capacity Limit**: The queue capacity is bounded (default: 200 jobs, via `ACESTEP_QUEUE_MAXSIZE`).
- **Overload Handling**: When the queue is full, incoming submissions are rejected with `HTTP 429 Too Many Requests ("Server busy: queue is full")` without creating orphaned records.
- **Worker Constraint**: Music generation is single-worker per GPU to prevent VRAM thrashing and CUDA context contention.

---

## 7. CORS & Network Security

- **CORS Configuration**: By default in development, CORS permits `localhost` and `127.0.0.1`. In production, CORS is restricted to explicitly configured origins defined in `DHAVLO_MI_CORS_ORIGINS` (or `SARIGAMA_CORS_ORIGINS`).
- **Network Exposure**: In production environments, never expose `0.0.0.0:8000` directly to the public internet. Always deploy behind a hardened reverse proxy with HTTPS.

---

## 8. Incident Response & Credential Rotation

If `DHAVLO_MI_API_KEY` is exposed:
1. Update `.env` with a newly generated high-entropy key:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
2. Restart the DHAVLO MI API server process:
   ```bash
   pkill -f "python.*api_server.py" && bash run_api_server.sh
   ```
3. Update downstream client configurations and integrations.

---

## 9. Reporting Security Vulnerabilities

Please report potential security issues privately:
- **GitHub Security Advisory**: Open a private advisory on the repository.
- Do not disclose unpatched vulnerabilities publicly.
