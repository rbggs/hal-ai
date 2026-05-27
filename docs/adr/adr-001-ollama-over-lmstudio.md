---
title: "ADR-001: LLM Runtime — Ollama over LM Studio"
tags: [adr, llm, ollama]
date: 2026-05-27
status: Accepted
---

# ADR-001: LLM Runtime — Ollama over LM Studio

**Date:** 2026-05-27
**Status:** Accepted

## Decision

Use **Ollama** as the local LLM runtime.

## Context

- Production target is an air-gapped Windows Server (no internet)
- Multi-user access via REST API required
- Must run headless — no desktop environment on server
- POC on Mac M4, same stack must deploy to prod unchanged

## Rejected: LM Studio

- Desktop app — no headless/server mode
- Not suited for Docker or service deployment
- API server mode is manual and not production-grade

## Consequences

- Ollama runs as a daemon with an OpenAI-compatible REST API on `:11434`
- Docker image available — fits into Compose stack
- Models pre-downloaded on connected machine, transferred as files to air-gapped server
- Metal GPU acceleration on M4 via llama.cpp — no extra config needed

## Related

- [[adr-003-skip-mlx]]
- [[requirements]]
