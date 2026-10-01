#!/bin/bash

"$(dirname "$0")/verify_deps.sh"

if [[ "$1" != "frontend" && "$1" != "backend" ]]; then
    printf 'You must specify a container to get a shell in.\nOptions: "frontend", "backend".\n'
    exit 1
fi

podman compose -f "$(dirname "$0")/../deploy/dev/docker/compose.yaml" exec "$1" /bin/sh
