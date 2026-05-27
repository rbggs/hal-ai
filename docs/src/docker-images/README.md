# docker-images/

Docker image tarballs saved with `docker save | gzip`.
Restore with `docker load < file.tar.gz`.

| File | Image | Tag |
|------|-------|-----|
| `ollama.tar.gz` | `ollama/ollama` | `latest` |
| `qdrant.tar.gz` | `qdrant/qdrant` | `latest` |
| `hal-api.tar.gz` | `hal-ai/api` | `latest` (built locally) |
| `hal-ui.tar.gz` | `hal-ai/ui` | `latest` (built locally) |

`hal-api.tar.gz` and `hal-ui.tar.gz` are produced by `scripts/bundle-app-images.sh` after the application Dockerfiles exist.
Not committed to git.
