#!/bin/bash

"$(dirname "$0")/verify_deps.sh"

podman compose -f "$(dirname "$0")/../deploy/dev/docker/compose.yaml" down -v
