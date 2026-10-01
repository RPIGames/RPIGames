#!/bin/bash
set -euo pipefail

# Gets a shell in a container. Needs an argument that specifies what container to spawn the shell in.

"$(dirname "$0")/verify_deps.sh"

if [[ "$1" != "frontend" && "$1" != "backend" ]]; then
    printf 'You must specify a container to get a shell in.\nOptions: "frontend", "backend".\n'
    exit 1
fi

podman compose \
    --file "$(dirname "$0")/../deploy/dev/docker/compose.yaml"\
   exec "$1" /bin/sh
