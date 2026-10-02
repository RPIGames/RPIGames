#!/bin/bash
set -euo pipefail

# Script that starts the docker compose

"$(dirname "$0")/verify_deps.sh"

SCRIPT_PATH=$(dirname "$0")/../deploy/dev/docker/compose.yaml
SCRIPT_PATH=$(realpath "$SCRIPT_PATH")

podman compose \
    --file "$SCRIPT_PATH" up \
    --force-recreate \
    --build \
    --detach
