# SARIGAMA Platform Architecture & Engineering Standards

## 1. Product Identity & Purpose

**SARIGAMA** is an open-source, AI-powered music creation and production platform. Designed for musicians, sound designers, content creators, and AI researchers, SARIGAMA turns natural language descriptions, genre tags, and lyrical prompts into studio-quality musical arrangements across 50+ languages.

Built on consumer-accessible hardware requirements (running locally in under 4GB of VRAM), SARIGAMA delivers commercial-grade synthesis with sub-2-second generation on high-end GPUs and rapid inference on Apple Silicon, AMD ROCm, and Intel XPU.

---

## 2. High-Level System Architecture

SARIGAMA employs a dual-stage neural architecture:

```
[ User Prompt / Lyrics / Audio Reference ]
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│           SARIGAMA Language Model Planner              │
│       (Chain-of-Thought Song Blueprinting)             │
│   • Generates BPM, key/scale, time signature           │
│   • Expands tags, structures lyrics into musical sections│
│   • Outputs structured DiT conditioning metadata       │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│            Diffusion Transformer (DiT) Engine          │
│   • FlowMatchEulerDiscreteScheduler (flow-matching)    │
│   • Audio latent generation across 10s to 10 minutes   │
│   • Tasks: Text2Music, Cover, Repaint, Stems, Lego     │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│          Continuous Latent Audio Codec (VAE)           │
│   • Decodes latents into high-fidelity stereo waveform │
│   • Output: 44.1kHz / 48kHz high-resolution audio      │
└────────────────────────────────────────────────────────┘
```

---

## 3. Repository Directory Map

```text
SARIGAMA/
├── assets/                     # Visual branding (logos, icons, architecture diagrams)
├── acestep/                    # Core foundation engine (retained module path)
│   ├── acestep_v15_pipeline.py # Gradio UI orchestration pipeline
│   ├── api_server.py           # FastAPI REST API server
│   ├── core/                   # DiT diffusion, conditioning, generation handlers
│   ├── models/                 # Model architecture definitions (DiT, VAE, LM)
│   ├── training/               # LoRA adapter training utilities
│   ├── training_v2/            # Advanced Side-Step training toolkit
│   ├── ui/gradio/              # Web UI components, styles, and i18n localizations
│   └── third_parts/            # Vendored dependencies (nano-vllm)
├── openrouter/                 # OpenRouter-compatible API proxy server
├── docs/                       # Multilingual documentation & VitePress site
├── scripts/                    # Hardware detection, benchmarks, audio tooling
├── cli.py                      # Interactive CLI music generation wizard
├── pyproject.toml              # Unified packaging specification (sarigama package)
├── docker-compose.yml          # Containerized deployment orchestration
├── THIRD_PARTY_NOTICES.md      # Comprehensive licensing inventory
├── NOTICE                      # Legal distribution notice
└── IDENTITY_AUDIT.md           # Detailed branding and technical identifier classification
```

---

## 4. Hardware Support & Runtime Matrix

SARIGAMA supports heterogeneous computing environments:

| Platform | Acceleration Backend | Min VRAM | Optimal Config |
|:---|:---|:---:|:---|
| **NVIDIA CUDA** | PyTorch / FlashAttention / vLLM | 4 GB | 8GB–24GB (Turbo/SFT DiT) |
| **Apple Silicon (macOS)** | Apple MLX (`mlx`, `mlx-lm`) / MPS | 8 GB Unified | M1/M2/M3/M4 Native Acceleration |
| **AMD ROCm** | ROCm PyTorch | 8 GB | Linux ROCm 6.x / Windows ROCm 3.12 |
| **Intel XPU** | Intel Extension for PyTorch (IPEX) | 8 GB | Arc GPUs / Intel Data Center GPUs |
| **CPU Fallback** | AVX-512 / OpenMP PyTorch | 16 GB RAM | Low-speed fallback mode |

---

## 5. Security & Operational Policy

1. **Credential Hygiene**: Never commit API keys, Hugging Face tokens, or external passphrases into Git. Store all secrets in local `.env` files (ignored by `.gitignore`).
2. **Local Binding**: Default servers (`Gradio`, `FastAPI`, `OpenRouter`) bind to `127.0.0.1` by default to avoid accidental exposure on local networks. To expose externally, use `--server-name 0.0.0.0` with explicit authentication (`--api-key`).
3. **Upload Sanitization**: Uploaded audio files for covers, repainting, and stem separation are validated for audio headers and written to temporary paths with safe permissions.
4. **Model Verification**: Weight downloads from authenticated repositories verify SHA256 checksums to guard against corrupted or tampered artifacts.

---

## 6. Contribution & Development Guidelines

1. **Scope Control**: Solve one problem per Pull Request. Do not bundle unrelated refactors or formatting changes.
2. **Preserve Compatibility**: Keep the `acestep` module namespace and `ACESTEP_*` environment variables intact for backward compatibility.
3. **Unit Testing**: Include unit tests under repository conventions (`*_test.py` or `test_*.py`). Validate locally using `uv run python -m unittest`.
4. **Documentation**: When adding features, update corresponding documentation under `docs/` and localized strings under `acestep/ui/gradio/i18n/`.
