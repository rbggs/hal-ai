---
title: "ADR-003: Skip MLX on Apple Silicon"
tags: [adr, mlx, ollama, mac]
date: 2026-05-27
status: Accepted
---

# ADR-003: Skip MLX on Apple Silicon

**Date:** 2026-05-27
**Status:** Accepted

## Decision

Do **not** use Apple MLX. Use Ollama on Apple Silicon.

## Context

- Dev machine is Mac M4 (Apple Silicon)
- Production is Windows Server — different architecture entirely
- Ollama already uses Metal GPU via llama.cpp on Apple Silicon

## Rejected: MLX

- Mac-only — does not run on Windows Server
- Introduces a dev/prod inference path divergence
- Not Docker-portable

## Consequences

- Ollama on M4 uses Metal acceleration automatically — no performance penalty
- Identical inference stack on dev (Mac) and prod (Windows Server)
- No code changes needed when moving POC to production

## Related

- [[adr-001-ollama-over-lmstudio]]
