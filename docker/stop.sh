#!/bin/bash
set -euo pipefail

# Stops the current podman compose session. Does not delete state.

"$(dirname "$0")/verify_deps.sh"

podman compose \
    --file "$(dirname "$0")/../deploy/dev/docker/compose.yaml" \
    down
