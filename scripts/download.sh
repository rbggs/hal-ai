#!/usr/bin/env bash
# Run on an internet-connected Mac to populate docs/src/ with all artifacts.
# After this completes, transfer docs/src/ to a USB drive or network share.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_DIR="$SCRIPT_DIR/../docs/src"

OLLAMA_MODELS=(
    "llama3.2:3b"
    "nomic-embed-text:latest"
)

DOCKER_IMAGES=(
    "ollama/ollama:latest"
    "qdrant/qdrant:latest"
)

log() { echo "[$(date +%H:%M:%S)] $*"; }
die() { echo "ERROR: $*" >&2; exit 1; }

check_deps() {
    local missing=()
    for cmd in curl docker ollama; do
        command -v "$cmd" &>/dev/null || missing+=("$cmd")
    done
    [[ ${#missing[@]} -eq 0 ]] || die "Missing: ${missing[*]}"
}

download_installers() {
    local dir="$BUNDLE_DIR/installers"
    log "Downloading Ollama installers..."
    [[ -f "$dir/Ollama-darwin.dmg" ]] || \
        curl -L --progress-bar "https://ollama.com/download/Ollama-darwin.dmg" -o "$dir/Ollama-darwin.dmg"
    [[ -f "$dir/OllamaSetup.exe" ]] || \
        curl -L --progress-bar "https://ollama.com/download/OllamaSetup.exe" -o "$dir/OllamaSetup.exe"
    log "Installers done."
}

pull_and_bundle_models() {
    local dir="$BUNDLE_DIR/ollama-models"
    log "Ensuring Ollama daemon is running..."
    if ! ollama list &>/dev/null; then
        die "Ollama not running. Start it: open /Applications/Ollama.app or 'ollama serve'"
    fi

    for model in "${OLLAMA_MODELS[@]}"; do
        local safe_name
        safe_name="$(echo "$model" | tr ':/' '--')"
        local out="$dir/${safe_name}.tar.gz"

        log "Pulling model: $model"
        ollama pull "$model"

        log "Bundling model: $model -> $out"
        # Determine the model's blob paths from the manifest
        local model_name="${model%%:*}"
        local model_tag="${model##*:}"
        local manifest_path="$HOME/.ollama/models/manifests/registry.ollama.ai/library/${model_name}/${model_tag}"

        if [[ ! -f "$manifest_path" ]]; then
            die "Manifest not found: $manifest_path"
        fi

        # Extract blob digests from manifest and bundle manifest + blobs
        local blob_digests
        blob_digests=$(python3 -c "
import json, sys
m = json.load(open('$manifest_path'))
digests = [m['config']['digest']] + [l['digest'] for l in m['layers']]
print('\n'.join(d.replace(':', '/') for d in digests))
")

        local tar_files=("models/manifests/registry.ollama.ai/library/${model_name}/${model_tag}")
        while IFS= read -r digest; do
            tar_files+=("models/blobs/$digest")
        done <<< "$blob_digests"

        tar -czf "$out" -C "$HOME/.ollama" "${tar_files[@]}"
        log "Bundled: $out ($(du -sh "$out" | cut -f1))"
    done
}

save_docker_images() {
    local dir="$BUNDLE_DIR/docker-images"
    for image in "${DOCKER_IMAGES[@]}"; do
        local safe_name
        safe_name="$(echo "$image" | tr ':/' '--' | sed 's/--latest//')"
        local out="$dir/${safe_name}.tar.gz"

        log "Pulling Docker image: $image"
        docker pull "$image"

        log "Saving: $image -> $out"
        docker save "$image" | gzip > "$out"
        log "Saved: $out ($(du -sh "$out" | cut -f1))"
    done
}

generate_checksums() {
    log "Generating checksums..."
    local out="$BUNDLE_DIR/checksums.sha256"
    # shasum is macOS; sha256sum is Linux — handle both
    local shabin
    shabin="$(command -v sha256sum 2>/dev/null || command -v shasum)"
    local shaflag=""
    [[ "$shabin" == *shasum ]] && shaflag="-a 256"

    (
        cd "$BUNDLE_DIR"
        find installers docker-images ollama-models -type f -not -name "*.md" | sort | \
            xargs $shabin $shaflag
    ) > "$out"
    log "Checksums written: $out"
}

main() {
    check_deps
    log "Bundle dir: $BUNDLE_DIR"
    download_installers
    pull_and_bundle_models
    save_docker_images
    generate_checksums
    log "Download complete. Transfer docs/src/ to target machine."
    log "Bundle size: $(du -sh "$BUNDLE_DIR" | cut -f1)"
}

main "$@"
