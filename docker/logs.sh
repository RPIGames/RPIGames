#!/bin/bash
set -euo pipefail

# Reads the logs of a container. Takes an optional argument
# for which container to get logs from. If empty, returns all.

"$(dirname "$0")/verify_deps.sh"

podman compose \
    --file "$(dirname "$0")/../deploy/dev/docker/compose.yaml" \
    logs "$1"
