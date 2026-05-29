#!/usr/bin/env bash
# Start all HAL-AI services: Ollama → Qdrant → Chainlit
# Air-gap safe: loads Qdrant image from docs/src/docker-images/qdrant.tar.gz
# Run from anywhere — script resolves PROJECT_ROOT from its own location.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
QDRANT_IMAGE_TAR="$PROJECT_ROOT/docs/src/docker-images/qdrant.tar.gz"
QDRANT_STORAGE="$HOME/qdrant_storage"
CHAINLIT_LOG="$PROJECT_ROOT/logs/chainlit.log"
OLLAMA_LOG="$PROJECT_ROOT/logs/ollama.log"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

ok()   { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}!${NC} $*"; }
die()  { echo -e "${RED}✗${NC} $*" >&2; exit 1; }
info() { echo "  $*"; }

mkdir -p "$PROJECT_ROOT/logs"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

wait_for_http() {
    local url="$1" label="$2" timeout="${3:-30}"
    local elapsed=0
    while ! curl -sf "$url" -o /dev/null 2>/dev/null; do
        if (( elapsed >= timeout )); then
            die "$label did not become ready within ${timeout}s"
        fi
        sleep 2; (( elapsed += 2 ))
        info "waiting for $label... (${elapsed}s)"
    done
}

container_exists() { podman container exists "$1" 2>/dev/null; }
image_exists()     { podman image exists "$1" 2>/dev/null; }

# ---------------------------------------------------------------------------
# 1. Ollama
# ---------------------------------------------------------------------------

echo
echo "=== Ollama ==="

if curl -sf http://localhost:11434/api/tags -o /dev/null 2>/dev/null; then
    ok "already running on :11434"
else
    command -v ollama &>/dev/null || die "ollama not installed — run scripts/deploy-offline.sh first"

    info "starting ollama serve..."
    nohup ollama serve > "$OLLAMA_LOG" 2>&1 &
    wait_for_http http://localhost:11434/api/tags "Ollama" 30
    ok "started (log: logs/ollama.log)"
fi

# ---------------------------------------------------------------------------
# 2. Qdrant
# ---------------------------------------------------------------------------

echo
echo "=== Qdrant ==="

command -v podman &>/dev/null || die "podman not installed — run: sudo apt install -y podman"

if curl -sf http://localhost:6333/healthz -o /dev/null 2>/dev/null; then
    ok "already running on :6333"
elif container_exists qdrant; then
    info "container exists but stopped — starting..."
    podman start qdrant
    wait_for_http http://localhost:6333/healthz "Qdrant" 30
    ok "started"
else
    # First-time setup — load image from bundle if not already pulled
    if ! image_exists qdrant/qdrant; then
        [[ -f "$QDRANT_IMAGE_TAR" ]] || \
            die "Qdrant image not found. Expected: $QDRANT_IMAGE_TAR\nRun scripts/download.sh on a connected machine first."
        info "loading Qdrant image from bundle (this takes ~30s)..."
        podman load < "$QDRANT_IMAGE_TAR"
        ok "image loaded"
    fi

    mkdir -p "$QDRANT_STORAGE"
    info "creating qdrant container..."
    podman run -d \
        --name qdrant \
        -p 6333:6333 \
        -p 6334:6334 \
        -v "$QDRANT_STORAGE:/qdrant/storage:z" \
        qdrant/qdrant:latest

    wait_for_http http://localhost:6333/healthz "Qdrant" 30
    ok "started (storage: $QDRANT_STORAGE)"
fi

# ---------------------------------------------------------------------------
# 3. Chainlit
# ---------------------------------------------------------------------------

echo
echo "=== Chainlit ==="

if curl -sf http://localhost:8080 -o /dev/null 2>/dev/null; then
    ok "already running on :8080"
else
    cd "$PROJECT_ROOT"

    # Ensure deps
    if ! python3 -m chainlit --version &>/dev/null; then
        warn "chainlit not installed — installing from requirements.txt..."
        pip3 install -q -r src/ui/requirements.txt \
            || die "pip install failed — check internet/proxy or pre-install deps offline"
    fi

    info "starting chainlit..."
    nohup python3 -m chainlit run src/ui/app.py --port 8080 --host 0.0.0.0 \
        > "$CHAINLIT_LOG" 2>&1 &
    wait_for_http http://localhost:8080 "Chainlit" 30
    ok "started (log: logs/chainlit.log)"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

echo
echo "=== All services up ==="
echo
echo "  Ollama   → http://localhost:11434"
echo "  Qdrant   → http://localhost:6333"
echo "  Chainlit → http://localhost:8080"
echo
