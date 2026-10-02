#!/bin/bash
set -euo pipefail

# Stops the current podman compose session. Does not delete state.

"$(dirname "$0")/verify_deps.sh"

SCRIPT_PATH=$(dirname "$0")/../deploy/dev/docker/compose.yaml
SCRIPT_PATH=$(realpath "$SCRIPT_PATH")

podman compose \
    --file "$SCRIPT_PATH" \
    down
