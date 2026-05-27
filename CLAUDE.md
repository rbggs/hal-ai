al# CLAUDE.md

## Audience

20+ year engineers and architects. Skip the basics.

## Writing Rules

- No corporate bloat — no "overview", "introduction", or "in summary" padding
- Tables and code blocks over prose
- If a sentence doesn't add information, delete it
- Document decisions, not motivations for obvious choices

## Code Rules

- No comments explaining what the code does — name things well instead
- No speculative abstractions — solve the problem at hand
- No feature flags, backwards-compat shims, or dead code
- Validate only at system boundaries

## File Management

- **Never delete or remove files** — move to `docs/archive/` instead
- Preserve original path as subdirectory under `docs/archive/` (e.g. `src/foo.py` → `docs/archive/src/foo.py`)
- If asked to delete, confirm with user and archive instead

## Project

- Stack: Ollama + Qdrant + LlamaIndex + FastAPI + Chainlit
- Deployment: Docker Compose, air-gapped Windows Server
- POC: Mac (Apple Silicon)
- Docs live in `docs/`, Obsidian-formatted Markdown

## Session Bootstrap

Run at the start of every session:
```bash
bd prime        # load beads session rules
bd ready        # see unblocked work
bd list --status=in_progress  # see what was in flight
```

### Current Phase
**Setup complete. Ready to write code.**

| Done | Item |
|------|------|
| ✓ | Requirements doc — `docs/requirements.md` |
| ✓ | ADRs (5) — `docs/adr/` |
| ✓ | Beads task hierarchy — 6 epics, 12 features, 28 tasks |
| ✗ | Code — nothing written yet |

### Next Action
Start with **Infrastructure epic** (`hal-ai-4ib`): Docker Compose stack + Ollama + Qdrant.
First task: `hal-ai-4ib.1.2` — `Write docker-compose.yml with all services`

### Beads Epic Map
| ID | Epic | Priority | Status |
|----|------|----------|--------|
| hal-ai-4ib | Infrastructure Setup | P0 | open — START HERE |
| hal-ai-zqf | Ingestion Pipeline | P0 | blocked by 4ib |
| hal-ai-rgb | RAG Query Engine | P1 | blocked by zqf |
| hal-ai-92k | API Layer | P1 | blocked by rgb |
| hal-ai-2ir | Chat UI | P2 | blocked by 92k |
| hal-ai-4st | Air-gap Deployment | P2 | blocked by 2ir |

### Key Decisions (see `docs/adr/` for full ADRs)
- Ollama over LM Studio (headless, Docker, Windows Server compatible)
- Qdrant over ChromaDB (100K+ docs, production-grade)
- No MLX (Mac-only, breaks dev/prod parity)
- No n8n (overkill for v1, FastAPI covers ingestion orchestration)
- LlamaIndex over LangChain (purpose-built for RAG)


<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:7510c1e2 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md for details and anti-patterns.

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->
