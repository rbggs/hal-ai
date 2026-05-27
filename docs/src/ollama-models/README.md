# ollama-models/

Ollama model blobs exported from `~/.ollama/models/`.

| File | Model | Size |
|------|-------|------|
| `llama3.2-3b.tar.gz` | `llama3.2:3b` | ~2 GB |
| `nomic-embed-text.tar.gz` | `nomic-embed-text:latest` | ~300 MB |

## How models are structured

Ollama stores models in `~/.ollama/models/` with two subdirs:
- `manifests/` — registry metadata (tiny)
- `blobs/` — actual weights (large)

The tarballs here capture both, preserving relative paths so they can be extracted directly into `~/.ollama/` on any machine.

## Restore

```bash
tar -xzf llama3.2-3b.tar.gz -C ~/.ollama/
tar -xzf nomic-embed-text.tar.gz -C ~/.ollama/
# Verify:
ollama list
```

Not committed to git.
