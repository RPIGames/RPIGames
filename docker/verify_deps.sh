#!/bin/bash

if ! command -v podman &> /dev/null;
  then echo "Podman installation not found. Please install podman."
  exit 1
fi

if command -v docker-compose >/dev/null 2>&1; then
    echo "docker-compose found"
elif command -v podman-compose >/dev/null 2>&1; then
    echo "podman-compose found"
else
    echo "No compose builder found, try installing podman-compose"
    exit 1
fi
