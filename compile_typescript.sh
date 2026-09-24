#!/bin/bash

if ! command -v tsc &> /dev/null;
  then echo "Typescript installation not found. Please install typescript."
  exit 1
fi

if command -v biome &> /dev/null; then
    biome check
else
    echo "Biome has not been found on PATH, so local linting will not run. You can instead rely on the remote github linter."
fi

tsc -p $(dirname "$0")"/src/frontend/tsconfig.json"
