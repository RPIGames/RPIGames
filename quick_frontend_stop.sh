#!/bin/bash

if ! command -v nginx &> /dev/null;
  then echo "Nginx not found. Please install nginx." 
  exit 1
fi

if [[ ! -f /tmp/nginx.pid ]]; then
  echo "Nginx hasn't been started yet. Cannot stop nginx."
  exit 1
fi

nginx -p . -c deploy/dev/nodocker/nginx_config_quick.conf -s stop
