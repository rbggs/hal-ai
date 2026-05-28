---
title: Ingestion & Qdrant Operations Runbook
tags: [operations, ingestion, qdrant]
created: 2026-05-28
---

# Ingestion & Qdrant Operations Runbook

## Prerequisites

All commands run from project root (`hal-ai/`).

| Requirement | Check |
|-------------|-------|
| Qdrant running | `curl http://localhost:6333/healthz` → `{"title":"qdrant"}` |
| Ollama running | `ollama list` → shows `gemma4:latest` and `nomic-embed-text:latest` |
| Python deps | `pip install -r src/rag/requirements.txt` |

---

## Qdrant Cleanup

### Option A — Wipe everything (full reset)

Use when: re-indexing all documents from scratch, schema change, or corrupt collection.

```bash
python scripts/qdrant_reset.py
```

Output:
```
Deleted:  hal_ai_docs
Created:  hal_ai_docs  (vector_size=768, distance=COSINE)
```

Collection is now empty. Re-ingest all documents after this.

---

### Option B — Remove one PDF's chunks only

Use when: re-ingesting a single updated document without disturbing others.

```bash
python scripts/qdrant_delete_source.py "volvo-trucks-basic-service-manual.pdf"
```

The argument must match the **filename exactly** (no path, just the filename). Check current sources:

```bash
# List all unique sources currently in Qdrant
python3 -c "
from qdrant_client import QdrantClient
from qdrant_client.models import Filter
c = QdrantClient(url='http://localhost:6333')
result = c.scroll('hal_ai_docs', limit=500, with_payload=True)
sources = sorted({p.payload.get('source','') for p in result[0]})
print('\n'.join(sources))
"
```

Output:
```
Deleted 163 chunks  (source='volvo-trucks-basic-service-manual.pdf')
Collection now has 0 chunks total.
```

---

## Ingestion

### Ingest all PDFs in `ingestions/`

Use for first-time setup or after wiping the collection.

```bash
cd src/rag
python ingest.py
```

What it does per PDF:
1. Extracts raster images → `data/figures/{source-slug}/page{N}_img{M}.png`
2. Chunks text by section heading (font-size detection)
3. Embeds each chunk (`nomic-embed-text:latest`)
4. Upserts to Qdrant with `text`, `source`, `section`, `subsection`, `page_start`, `page_end`, `figures[]`

Expected output for the Volvo manual:
```
[pdf] volvo-trucks-basic-service-manual.pdf
  Extracted 169 images → data/figures/volvo-trucks-basic-service-manual/
  163 chunks
  Skipped 19 stub chunks (< 50 chars)
  163 points upserted

Done — 163 total chunks in 'hal_ai_docs'
```

---

### Ingest a single PDF

```bash
cd src/rag
python ingest.py ../../ingestions/volvo-trucks-basic-service-manual.pdf
```

---

### Add a new PDF

1. Copy PDF into `ingestions/`
2. Run ingestion (single file or full):

```bash
cp /path/to/new-manual.pdf ingestions/
cd src/rag && python ingest.py ../../ingestions/new-manual.pdf
```

Images extract to `data/figures/new-manual/` automatically. No other configuration needed.

---

### Re-ingest an updated PDF (replace in place)

```bash
# 1. Remove old chunks
python scripts/qdrant_delete_source.py "my-manual.pdf"

# 2. Remove old extracted images
rm -rf data/figures/my-manual/

# 3. Re-ingest
cd src/rag && python ingest.py ../../ingestions/my-manual.pdf
```

---

## Common Scenarios

| Scenario | Steps |
|----------|-------|
| First-time setup | Reset → Ingest all |
| Added a new PDF | Ingest single file |
| Updated an existing PDF | Delete source → Remove figures dir → Ingest single file |
| Schema/collection change | Reset → Ingest all |
| Something looks wrong with one doc | Delete source → Ingest single file |
| Start completely fresh | Reset → Delete `data/figures/` → Ingest all |

---

## Verify Collection State

```bash
python3 -c "
from qdrant_client import QdrantClient
c = QdrantClient(url='http://localhost:6333')
info = c.get_collection('hal_ai_docs')
print(f'Vectors:  {info.vectors_count}')
print(f'Points:   {info.points_count}')
print(f'Status:   {info.status}')
"
```

---

## File Locations

| Path | Contents |
|------|----------|
| `ingestions/` | Source PDFs — drop new documents here |
| `data/figures/{slug}/` | Extracted images — auto-created during ingestion |
| `scripts/qdrant_reset.py` | Full collection wipe + recreate |
| `scripts/qdrant_delete_source.py` | Per-source chunk deletion |
| `src/rag/ingest.py` | Ingestion entry point |
| `src/rag/pdf_ingest.py` | PDF extraction + chunking + image logic |
