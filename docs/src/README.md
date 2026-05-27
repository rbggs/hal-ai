# docs/src — Offline Artifact Bundle

All downloadable artifacts needed to stand up the HAL-AI stack on an air-gapped machine.

**Workflow:**
1. Run `scripts/download.sh` on an internet-connected Mac
2. Copy this entire `docs/src/` directory to a USB drive or network share
3. On the target machine, run `scripts/deploy-offline.sh` (Mac/Linux) or `scripts/deploy-offline.ps1` (Windows Server)

## Directory Map

| Directory | Contents | Source |
|-----------|----------|--------|
| `installers/` | Ollama binaries (.dmg, .exe) | ollama.com |
| `docker-images/` | Docker image tarballs (.tar.gz) | Docker Hub |
| `ollama-models/` | Ollama model blobs (.tar.gz) | pulled via `ollama pull` |

## What Gets Downloaded

| Artifact | File | Size (approx) |
|----------|------|----------------|
| Ollama macOS app | `installers/Ollama-darwin.dmg` | ~200 MB |
| Ollama Windows installer | `installers/OllamaSetup.exe` | ~200 MB |
| Docker image: ollama/ollama | `docker-images/ollama.tar.gz` | ~1.5 GB |
| Docker image: qdrant/qdrant | `docker-images/qdrant.tar.gz` | ~100 MB |
| Ollama model: llama3.2:3b | `ollama-models/llama3.2-3b.tar.gz` | ~2 GB |
| Ollama model: nomic-embed-text | `ollama-models/nomic-embed-text.tar.gz` | ~300 MB |

## Git Ignore

Binary artifacts are gitignored — only scripts and READMEs are tracked.
Transfer `docs/src/` out-of-band (USB, LAN share, S3 bucket on connected side).

## Checksums

`scripts/bundle-check.sh` verifies SHA-256 of all artifacts against `docs/src/checksums.sha256`.
Run it after download and again after transfer to confirm integrity.
