---
title: Prerequisites
tags: [deploy, install]
---

# Prerequisites

## Hardware

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 8 cores | 16 cores |
| RAM | 16 GB | 32 GB |
| Disk | 50 GB free | 100 GB free |
| GPU | Not required | NVIDIA (speeds up Ollama) |

## Software

| Component | Version | Notes |
|-----------|---------|-------|
| Windows Server | 2019 or 2022 | WSL2 must be enabled |
| WSL2 | Ubuntu 22.04 LTS | Install from Microsoft Store |
| Podman | 4.x+ | Installed inside WSL2 |
| Python | 3.11+ | Inside WSL2 |
| Ollama | Latest | Inside WSL2 |

## Ports Required

| Port | Service | Direction |
|------|---------|-----------|
| 6333 | Qdrant REST API | Internal only |
| 6334 | Qdrant gRPC | Internal only |
| 11434 | Ollama API | Internal only |
| 8080 | Chainlit UI | Expose to users |
| 8001 | FastAPI backend | Internal only |

## Disk Layout

```
C:\qdrant_storage\     ← Qdrant vector DB persistent storage
~/hal-ai/              ← Application (inside WSL2)
~/.ollama/             ← Ollama models (inside WSL2)
```
