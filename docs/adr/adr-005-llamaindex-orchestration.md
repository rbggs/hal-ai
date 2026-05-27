---
title: "ADR-005: LlamaIndex for RAG Orchestration"
tags: [adr, llamaindex, rag]
date: 2026-05-27
status: Accepted
---

# ADR-005: LlamaIndex for RAG Orchestration

**Date:** 2026-05-27
**Status:** Accepted

## Decision

Use **LlamaIndex** for RAG pipeline orchestration.

## Context

- Need: document loading, chunking, embedding, retrieval, and query synthesis
- Local-only stack — no external API calls
- Qdrant as vector store, Ollama as LLM + embedding provider

## LlamaIndex vs LangChain

| | LlamaIndex | LangChain |
|--|-----------|-----------|
| RAG focus | Purpose-built | General-purpose, heavier |
| Qdrant integration | First-class | Available |
| Ollama integration | First-class | Available |
| Abstractions for ingestion | Strong (SimpleDirectoryReader, node parsers) | Requires more wiring |
| Complexity for pure RAG | Lower | Higher |

## Consequences

- `VectorStoreIndex` + `QdrantVectorStore` handles indexing and retrieval
- `OllamaEmbedding` + `Ollama` LLM wired via `Settings`
- Document loaders: `SimpleDirectoryReader` for files, custom readers for other sources
- Query pipeline: retrieve top-k chunks → synthesize with LLM → return with source nodes

## Related

- [[adr-002-qdrant-over-chromadb]]
- [[adr-001-ollama-over-lmstudio]]
