#!/bin/bash
set -euo pipefail

# Script that resets the database and in the future all mutable state.
# Also turns off the server.

"$(dirname "$0")/verify_deps.sh"

podman compose \
    --file "$(dirname "$0")/../deploy/dev/docker/compose.yaml" \
    down \
    --volumes
