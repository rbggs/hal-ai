---
title: HAL-AI Requirements
tags: [requirements, architecture]
created: 2026-05-27
status: draft
---

# HAL-AI — Local RAG Chatbot

## Context

Fully air-gapped RAG chatbot. No external API calls in production. POC on Mac, deploy to Windows Server.

## Functional Requirements

| ID  | Requirement                                                      |
| --- | ---------------------------------------------------------------- |
| F1  | Ingest documents (PDF, Word, plain text) into local vector store |
| F2  | Chunk, embed, and index documents via local embedding model      |
| F3  | Accept natural language queries and return grounded answers      |
| F4  | Support multi-user concurrent access via REST API                |
| F5  | Source attribution — responses cite ingested documents           |
| F6  | Re-ingestion / update support without full re-index              |

## Non-Functional Requirements

| ID  | Requirement                                             |
| --- | ------------------------------------------------------- |
| N1  | Fully offline — zero internet dependency at runtime     |
| N2  | All models and data stored locally on-prem              |
| N3  | Scale to 100K+ documents without degradation            |
| N4  | Docker Compose deployable on Windows Server             |
| N5  | POC portable from Mac (Apple Silicon) to Windows Server |

## Constraints

- No cloud LLM APIs (OpenAI, Anthropic, etc.)
- Windows Server has no internet access — all artifacts pre-downloaded
- Mac used for development/POC only

## Stack Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| LLM runtime | Ollama | Headless daemon, OpenAI-compatible API, Docker-ready |
| LLM model | Llama 3.2 / Mistral 7B | Balance of quality vs. hardware |
| Embeddings | nomic-embed-text (Ollama) | Local, high quality, 768-dim |
| Vector DB | Qdrant | Production-grade, handles 100K+ docs, Docker |
| Orchestration | LlamaIndex | Clean RAG abstractions |
| Backend | FastAPI | Async, OpenAPI spec auto-generated |
| UI | Chainlit | Chat UI, minimal setup |
| Packaging | Docker Compose | Single-stack deployment |

## Out of Scope

- Fine-tuning / RLHF
- Multi-modal (images, audio)
- Auth / RBAC (v1)

## Open Questions

- [ ] Document sources — filesystem mount, upload API, or both?
- [ ] GPU available on Windows Server? (affects model size choice)
- [ ] Target response latency SLA?
- [ ] Qdrant: single-node or clustered?

## Related

- [[architecture]]
- [[deployment]]
- [[ingestion-pipeline]]
