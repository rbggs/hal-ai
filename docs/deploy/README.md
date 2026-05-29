---
title: Deployment Guide
tags: [deploy]
---

# Deployment Guide

## Install Order

| Step | Document | What |
|------|----------|------|
| 1 | [prerequisites.md](prerequisites.md) | Hardware, OS, port requirements |
| 2 | [wsl2-podman-qdrant.md](wsl2-podman-qdrant.md) | WSL2 + Podman + Qdrant |
| 3 | [ollama-setup.md](ollama-setup.md) | Ollama + models |
| 4 | [app-setup.md](app-setup.md) | Python deps + ingest + UI |

## Stack

```
Windows Server
└── WSL2 (Ubuntu 22.04)
    ├── Podman
    │   └── qdrant:latest          → localhost:6333
    ├── Ollama                     → localhost:11434
    │   ├── gemma4:latest          (9.6 GB — LLM)
    │   └── nomic-embed-text:latest (274 MB — embeddings)
    └── Python app
        ├── src/rag/ingest.py      (ingestion pipeline)
        └── src/ui/app.py          (Chainlit UI → localhost:8080)
```

## Quick Start

After all services are installed:
```bash
bash scripts/start.sh
```
Checks each service, starts anything that's down. Safe to run repeatedly.

## Quick Health Check

```bash
curl http://localhost:6333/healthz   # Qdrant
curl http://localhost:11434/api/tags # Ollama
curl http://localhost:8080           # UI
```

## Ingest Documents

Drop PDFs or XMLs into `ingestions/`, then:
```bash
python3 src/rag/ingest.py
```

## Air-gap

All artifacts must be pre-downloaded on a machine with internet access:
```bash
bash scripts/download.sh        # download models + images
bash scripts/deploy-offline.sh  # install from bundle (no internet needed)
```

See `docs/src/README.md` for bundle contents.
