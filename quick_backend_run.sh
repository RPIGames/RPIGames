#!/bin/bash

if ! command -v uv &> /dev/null;
  then echo "uv not found. Please install uv." 
  exit 1
fi

uv run --directory src/backend fastapi dev
