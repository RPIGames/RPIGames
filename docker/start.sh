#!/bin/bash
set -euo pipefail

"$(dirname "$0")/verify_deps.sh"

podman compose --file "$(dirname "$0")/../deploy/dev/docker/compose.yaml" up --force-recreate --build -d
