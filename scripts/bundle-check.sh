#!/usr/bin/env bash
# Verify bundle integrity against checksums.sha256.
# Run after download and again after transfer to the target machine.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_DIR="$SCRIPT_DIR/../docs/src"
CHECKSUM_FILE="$BUNDLE_DIR/checksums.sha256"

die() { echo "ERROR: $*" >&2; exit 1; }

[[ -f "$CHECKSUM_FILE" ]] || die "No checksums.sha256 found. Run scripts/download.sh first."

# shasum is macOS; sha256sum is Linux
shabin="$(command -v sha256sum 2>/dev/null || command -v shasum)"
shaflag=""
[[ "$shabin" == *shasum ]] && shaflag="-a 256"

echo "Verifying bundle: $BUNDLE_DIR"
(
    cd "$BUNDLE_DIR"
    $shabin $shaflag --check "$CHECKSUM_FILE"
)
echo "All checksums OK."
