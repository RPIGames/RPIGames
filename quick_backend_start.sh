#!/bin/bash

if ! command -v uv &> /dev/null;
  then echo "uv not found. Please install uv."
  exit 1
fi

# run tests
uv run --project src/backend/ coverage run -m pytest
uv run --project src/backend/ coverage json -q -o /dev/stdout | jq -r '"Code Coverage: \(.totals.percent_covered)"'

uv run --directory src/backend fastapi dev
