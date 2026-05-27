#!/usr/bin/env bash
# Install HAL-AI stack from docs/src/ on an air-gapped Mac or Linux machine.
# Run AFTER transferring docs/src/ to this machine.
# Requires: Podman installed and machine running (Mac), or Podman installed (Linux)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_DIR="$SCRIPT_DIR/../docs/src"

PLATFORM="$(uname -s)"  # Darwin or Linux

log() { echo "[$(date +%H:%M:%S)] $*"; }
die() { echo "ERROR: $*" >&2; exit 1; }

[[ -d "$BUNDLE_DIR" ]] || die "Bundle dir not found: $BUNDLE_DIR"

verify_bundle() {
    log "Verifying bundle checksums..."
    "$SCRIPT_DIR/bundle-check.sh"
}

install_ollama_mac() {
    local dmg="$BUNDLE_DIR/installers/Ollama-darwin.dmg"
    [[ -f "$dmg" ]] || die "Missing: $dmg"

    if [[ -d /Applications/Ollama.app ]]; then
        log "Ollama.app already installed, skipping."
        return
    fi

    log "Installing Ollama from $dmg..."
    hdiutil attach "$dmg" -quiet
    cp -r /Volumes/Ollama/Ollama.app /Applications/
    hdiutil detach /Volumes/Ollama -quiet
    log "Ollama installed. Launch: open /Applications/Ollama.app"
}

install_ollama_linux() {
    die "Linux native install not automated. Restore Ollama models and run 'ollama serve' manually."
}

load_container_images() {
    log "Loading container images via Podman..."
    for tar in "$BUNDLE_DIR/docker-images/"*.tar.gz; do
        [[ -f "$tar" ]] || continue
        log "Loading: $(basename "$tar")"
        podman load < "$tar"
    done
    log "Images loaded."
    podman images
}

restore_ollama_models() {
    log "Restoring Ollama models to ~/.ollama/..."
    mkdir -p "$HOME/.ollama"
    for tar in "$BUNDLE_DIR/ollama-models/"*.tar.gz; do
        [[ -f "$tar" ]] || continue
        log "Restoring: $(basename "$tar")"
        tar -xzf "$tar" -C "$HOME/.ollama/"
    done
    log "Models restored."
    ollama list 2>/dev/null || log "(Start Ollama daemon to verify: ollama list)"
}

main() {
    verify_bundle

    case "$PLATFORM" in
        Darwin) install_ollama_mac ;;
        Linux)  install_ollama_linux ;;
        *) die "Unsupported platform: $PLATFORM" ;;
    esac

    load_container_images
    restore_ollama_models

    log "Offline deployment complete."
    log "Next: cd project root && podman compose up -d"
}

main "$@"
