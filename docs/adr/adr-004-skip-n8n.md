---
title: "ADR-004: Skip n8n for Orchestration"
tags: [adr, n8n, ingestion]
date: 2026-05-27
status: Accepted
---

# ADR-004: Skip n8n for Orchestration

**Date:** 2026-05-27
**Status:** Accepted

## Decision

Do **not** add n8n. Handle ingestion orchestration in FastAPI.

## Context

- All document ingestion consumers are technical (engineers)
- Ingestion sources: filesystem mount and/or upload API (TBD)
- FastAPI + LlamaIndex already covers the ingestion pipeline

## Rejected: n8n

- Extra service, extra Docker container, extra failure surface
- All n8n triggers (folder watch, schedule, webhook) can be implemented directly in FastAPI with Watchdog / APScheduler
- No non-technical users wiring up workflows in v1

## Revisit If

- Non-technical users need to manage document sources via GUI
- Ingestion sources grow to 10+ heterogeneous systems requiring visual wiring

## Consequences

- Ingestion triggered via `POST /ingest` or folder watcher in FastAPI service
- Scheduled re-indexing via APScheduler inside the app
- Simpler stack — one fewer service to deploy and monitor

## Related

- [[requirements]]
- [[adr-005-llamaindex-orchestration]]
