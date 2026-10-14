# SARIGAMA Identity-Consistency Audit & Technical Classification

This audit documents the systematic classification of upstream `ACE-Step` references and explains the rationale for every retained identifier, updated brand element, and legal attribution notice.

---

## Classification Taxonomy

| Category | Description | Policy |
|:---:|:---|:---|
| **A** | **User-Facing Branding** | Replaced with **SARIGAMA** (titles, banners, CLI wizards, app subtitles, package display). |
| **B** | **Technical Identifier** | **Retained** for backward compatibility (environment variables `ACESTEP_*`, module path `acestep.*`, checkpoint filenames, internal API keys). |
| **C** | **Required Legal Notice** | **Preserved intact** (MIT License notices, copyright of upstream authors, original bibtex citations). |
| **D** | **Upstream Source Reference** | **Retained & labeled** (Hugging Face model repository paths `ACE-Step/Ace-Step1.5`, technical paper references). |
| **E** | **Obsolete / Dead Reference** | **Removed / Replaced** (dead website links, incorrect upstream issue links, obsolete badges). |
| **F** | **Investigated Boundary** | Audited and verified safe without breaking downstream or platform compatibility. |

---

## Detailed Classification Register

### 1. Project-Level Branding & Metadata (Category A)
- **`README.md` Title & Hero**: Updated from `ACE-Step 1.5` to `🎵 SARIGAMA — Next-Generation Open-Source AI Music Generation Foundation Model`. (Category A)
- **`pyproject.toml`**: `project.name = "sarigama"`, `description = "SARIGAMA: Next-Generation Open-Source Music Generation Foundation Model"`. Added scripts `sarigama`, `sarigama-api`, `sarigama-download`, `sarigama-openrouter` alongside backward-compatible aliases `acestep*`. (Category A & B)
- **`package.json`**: Package name set to `"sarigama"`. (Category A)
- **Gradio Web UI (`acestep/ui/gradio/i18n/*.json`)**: App title updated to `🎵 SARIGAMA Studio 💡` across all 5 localization bundles (`en.json`, `zh.json`, `ja.json`, `pt.json`, `he.json`). (Category A)
- **FastAPI Documentation (`acestep/api_server.py`)**: `title="SARIGAMA API"`, `version="1.5.0"`. (Category A)
- **OpenRouter Server (`openrouter/openrouter_api_server.py`)**: `MODEL_NAME = "SARIGAMA"`, `title="SARIGAMA OpenRouter API"`. (Category A)
- **Interactive CLI Wizard (`cli.py`)**: Welcome banner updated to `"Welcome to the SARIGAMA Music Generation Wizard!"`. (Category A)
- **Launch Scripts (`start_*.sh`, `start_*.bat`)**: Banners updated to `"Starting SARIGAMA"`. (Category A)
- **Docker Compose (`docker-compose.yml`)**: Header updated to `SARIGAMA — Docker Compose`. (Category A)

### 2. Technical Compatibility Identifiers Retained (Category B)
- **Module Namespace (`acestep.*`)**: Preserved. Renaming the Python package directory would break hundreds of internal imports, downstream integrations, ComfyUI nodes, and external scripts.
- **Environment Variables**:
  - `ACESTEP_CONFIG_PATH`
  - `ACESTEP_LM_MODEL_PATH`
  - `ACESTEP_INIT_LLM`
  - `ACESTEP_DOWNLOAD_SOURCE`
  - `ACESTEP_CHECKPOINTS_DIR`
  *Policy: Retained so existing user configurations, `.env` files, and deployment scripts continue to function seamlessly.*
- **Model Checkpoints**: Model weights downloaded from Hugging Face use standard IDs (`acestep-v15-turbo`, `acestep-v15-sft`, `acestep-5Hz-lm-*`). Modifying internal weights names would break automated Hugging Face downloads.
- **CLI Backward Compatibility**: CLI script aliases `acestep` and `acestep-api` remain registered alongside `sarigama` and `sarigama-api`.

### 3. Legal Attribution & Copyright Preserved (Category C)
- **Root `LICENSE`**: Preserves `Copyright (c) 2026 ACEStep` alongside `Copyright (c) 2026 SARIGAMA Contributors`.
- **`THIRD_PARTY_NOTICES.md`**: Complete inventory attributing ACE-Step 1.5 (MIT), nano-vllm (MIT by Xingkai Yu), and base model weights.
- **`NOTICE`**: Explicit attribution notice for distribution compliance.
- **`README.md` Research Citation**: Retains BibTeX citation acknowledging the original foundation architecture authors (Gong et al., 2026).

### 4. Upstream Source References (Category D)
- **Hugging Face Checkpoints**: `https://huggingface.co/ACE-Step/Ace-Step1.5` explicitly credited as the upstream model repository.
- **Technical Report**: Link to arXiv paper `arXiv:2602.00744` retained for academic grounding.

---

## Audit Verification Summary
- **No breaking module alterations**: Python package execution paths remain 100% stable.
- **Zero orphaned references in core interfaces**: Gradio, FastAPI, OpenRouter, and CLI all identify as SARIGAMA.
- **100% License compliance**: Upstream rights preserved in accordance with the MIT License.
