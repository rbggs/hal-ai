---
title: "ADR-002: Vector DB — Qdrant over ChromaDB"
tags: [adr, vectordb, qdrant]
date: 2026-05-27
status: Accepted
---

# ADR-002: Vector DB — Qdrant over ChromaDB

**Date:** 2026-05-27
**Status:** Accepted

## Decision

Use **Qdrant** as the vector database.

## Context

- Target corpus: 100K+ documents
- Multi-user, concurrent read/write
- Must run as a persistent service in Docker Compose
- Air-gapped Windows Server deployment

## Rejected: ChromaDB

- In-memory by default — persistent mode is fragile at scale
- No gRPC, limited filtering capabilities
- Not designed for 100K+ doc production workloads
- Community/dev-grade; lacks operational maturity

## Consequences

- Qdrant runs as a Docker service, REST on `:6333`, gRPC on `:6334`
- Persistent storage via Docker volume mount
- Supports payload filtering — useful for multi-tenant or doc-type scoping
- `qdrant-client` Python SDK integrates cleanly with LlamaIndex

## Related

- [[requirements]]
- [[adr-005-llamaindex-orchestration]]
