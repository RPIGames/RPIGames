#!/bin/bash

if ! command -v nginx &> /dev/null;
  then echo "Nginx not found. Please install nginx."
  exit 1
fi

if [[ -f /tmp/nginx.pid ]]; then
  echo "Nginx has already been started. Attempting to restart nginx..."

  ./quick_frontend_stop.sh

  if [[ "$?" -ne 0 ]]; then
    echo "Nginx could not be stopped. Stop nginx or delete /tmp/nginx.pid if nginx stopped incorrectly."
    exit 1
  fi
fi

./compile_typescript.sh

nginx -p . -c deploy/dev/nodocker/nginx_config_quick.conf 2> /dev/null
printf "Frontend should be started at http://localhost:5000/\n"
