---
tags:
  - daily_notes
---
# Requirements for HAL-Ai chatbot
- at 11:30 #Suren gave the requirements


# Action items 
- Ollama
- ChromaDB
- beads 
- n8n
-

---

# Session Log — 2026-05-27

## Completed

| Task | Detail |
|------|--------|
| Ollama installed | Native macOS app, Metal GPU, daemon on `:11434` |
| Models pulled | `gemma4:latest` (9.6 GB), `nomic-embed-text:latest` (274 MB) |
| Model decision | Switched from `llama3.2:3b` → `gemma4:latest` — better instruction following |
| Air-gap bundle | `docs/src/` structure + `scripts/download.sh`, `bundle-check.sh`, `deploy-offline.sh`, `deploy-offline.ps1` |
| Chainlit UI spike | `src/ui/app.py` — streams gemma4 responses, multi-turn history, running on `:8001` |
| Docs updated | `docs/requirements.md`, `CLAUDE.md`, `docs/constitutional-log.md` |

## Beads Closed
- `hal-ai-4ib.2.1` — Pull nomic-embed-text
- `hal-ai-4ib.2.2` — Pull llama3.2 (pulled gemma4 instead)
- `hal-ai-2ir.1.1` — Chainlit UI spike
- `hal-ai-4st.1.1` — Ollama model export script
- `hal-ai-4st.1.3` — Docker save/load scripts

## Next Session
`hal-ai-4ib.1.2` — Write `docker-compose.yml` (Ollama + Qdrant + FastAPI + Chainlit) 