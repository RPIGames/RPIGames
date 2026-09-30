#!/bin/bash

if ! command -v uv &> /dev/null;
  then echo "uv not found. Please install uv." 
  exit 1
fi

# run tests
uv --project src/backend run pytest

uv run --directory src/backend fastapi dev
