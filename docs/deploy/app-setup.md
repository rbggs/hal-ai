---
title: Application Setup
tags: [deploy, install, app]
---

# Application Setup

Assumes Qdrant and Ollama are running. See:
- [`wsl2-podman-qdrant.md`](wsl2-podman-qdrant.md)
- [`ollama-setup.md`](ollama-setup.md)

---

## 1. Clone / Transfer Project

**With internet:**
```bash
git clone <repo-url> ~/hal-ai
cd ~/hal-ai
```

**Air-gap:** transfer the project directory via USB or network share, then:
```bash
cd ~/hal-ai
```

---

## 2. Install Python Dependencies

```bash
# Ingestion pipeline
pip install -r src/rag/requirements.txt

# Chainlit UI
pip install -r src/ui/requirements.txt
```

`src/rag/requirements.txt`:
```
qdrant-client
ollama
pdfplumber
pillow
```

`src/ui/requirements.txt`:
```
chainlit
ollama
qdrant-client
```

---

## 3. Ingest Documents

Drop PDF or XML files into `ingestions/`, then:

```bash
# Ingest all documents
python3 src/rag/ingest.py

# Ingest a single file
python3 src/rag/ingest.py ingestions/my-manual.pdf
```

Expected output:
```
[pdf] service-manual-eats.pdf
  Extracted 157 images → data/figures/service-manual-eats-/
  67 chunks  (doc_title='36. EATs')
  67 points upserted

Done — 67 total chunks in 'hal_ai_docs'
```

---

## 4. Start the UI

```bash
cd src/ui
python3 -m chainlit run app.py --port 8000
```

Open browser: `http://localhost:8000`

For remote access (Windows host accessing WSL2):
```
http://<windows-ip>:8000
```

---

## 5. Verify Everything Works

```bash
# Qdrant
curl http://localhost:6333/healthz

# Ollama
curl http://localhost:11434/api/tags

# Point count in Qdrant
python3 -c "from qdrant_client import QdrantClient; c = QdrantClient(url='http://localhost:6333'); print('Points:', c.get_collection('hal_ai_docs').points_count)"

# UI
curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost:8000
# → HTTP 200
```

---

## 6. Qdrant Collection Management

```bash
# Full reset (wipe all data)
python3 scripts/qdrant_reset.py

# Remove one document's chunks
python3 scripts/qdrant_delete_source.py "my-manual.pdf"
```

See [`operations/ingestion-runbook.md`](../operations/ingestion-runbook.md) for full operations reference.
