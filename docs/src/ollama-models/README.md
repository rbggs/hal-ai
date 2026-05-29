# ollama-models/

Ollama model blobs exported from `~/.ollama/models/`.

| File | Model | Size |
|------|-------|------|
| `gemma4--latest.tar.gz` | `gemma4:latest` | ~9.6 GB |
| `nomic-embed-text--latest.tar.gz` | `nomic-embed-text:latest` | ~300 MB |

## How models are structured

Ollama stores models in `~/.ollama/models/` with two subdirs:
- `manifests/` — registry metadata (tiny)
- `blobs/` — actual weights (large)

The tarballs here capture both, preserving relative paths so they can be extracted directly into `~/.ollama/` on any machine.

## Restore

```bash
tar -xzf gemma4--latest.tar.gz -C ~/.ollama/
tar -xzf nomic-embed-text--latest.tar.gz -C ~/.ollama/
# Verify:
ollama list
```

Not committed to git.
