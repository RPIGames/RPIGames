#!/bin/bash
set -euo pipefail

# Script that starts the docker compose

"$(dirname "$0")/verify_deps.sh"

podman compose \
    --file "$(dirname "$0")/../deploy/dev/docker/compose.yaml" up \
    --force-recreate \
    --build \
    --detach
