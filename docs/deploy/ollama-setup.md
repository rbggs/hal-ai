---
title: Ollama Setup
tags: [deploy, install, ollama]
---

# Ollama Setup

## 1. Install Ollama (WSL2 / Linux)

```bash
curl -fsSL https://ollama.com/install.sh | sh

# Verify
ollama --version
```

Start the Ollama daemon:
```bash
ollama serve &     # background
# or
nohup ollama serve > ~/ollama.log 2>&1 &
```

---

## 2. Pull Required Models

```bash
ollama pull nomic-embed-text:latest    # 274 MB — embeddings
ollama pull gemma4:latest              # 9.6 GB — LLM
```

Verify:
```bash
ollama list
# NAME                       ID              SIZE
# gemma4:latest              c6eb396dbd59    9.6 GB
# nomic-embed-text:latest    0a109f422b47    274 MB
```

---

## 3. Air-gap install (no internet)

Models are stored in `~/.ollama/models/`. Transfer from a machine that has them:

```bash
# On source machine — pack models
tar -czf ollama-models.tar.gz -C ~/.ollama models/

# Transfer ollama-models.tar.gz to target machine, then:
mkdir -p ~/.ollama
tar -xzf ollama-models.tar.gz -C ~/.ollama/

# Verify
ollama list
```

Or use the project's offline deploy script:
```bash
bash scripts/deploy-offline.sh
```

---

## 4. Auto-start Ollama

**With systemd:**
```bash
sudo tee /etc/systemd/system/ollama.service > /dev/null <<EOF
[Unit]
Description=Ollama Service
After=network.target

[Service]
ExecStart=/usr/local/bin/ollama serve
Restart=always
User=$USER

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now ollama.service
```

**Without systemd** — add to `~/.bashrc`:
```bash
echo 'ollama serve > ~/ollama.log 2>&1 &' >> ~/.bashrc
```

---

## Models Reference

| Model | Size | Purpose |
|-------|------|---------|
| `nomic-embed-text:latest` | 274 MB | Converts text to 768-dim vectors for Qdrant |
| `gemma4:latest` | 9.6 GB | Generates answers + query expansion |

Both must be running before starting the application.

Verify both are available:
```bash
curl http://localhost:11434/api/tags
```
