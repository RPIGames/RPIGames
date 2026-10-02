#!/bin/bash
set -euo pipefail

# Reads the logs of a container. Takes an optional argument
# for which container to get logs from. If empty, returns all.

"$(dirname "$0")/verify_deps.sh"

SCRIPT_PATH=$(dirname "$0")/../deploy/dev/docker/compose.yaml
SCRIPT_PATH=$(realpath "$SCRIPT_PATH")

podman compose \
    --file "$SCRIPT_PATH" \
    logs "$1"
