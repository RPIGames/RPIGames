#!/bin/bash

if ! command -v tsc &> /dev/null;
  then echo "Typescript installation not found. Please install typescript." 
  exit 1
fi

tsc -p $(dirname "$0")"/src/frontend"