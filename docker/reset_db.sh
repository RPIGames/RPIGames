#!/bin/bash
set -euo pipefail

# Script that resets the database and in the future all mutable state.
# Also turns off the server.

"$(dirname "$0")/verify_deps.sh"

SCRIPT_PATH=$(dirname "$0")/../deploy/dev/docker/compose.yaml
SCRIPT_PATH=$(realpath "$SCRIPT_PATH")

podman compose \
    --file "$SCRIPT_PATH" \
    down \
    --volumes
