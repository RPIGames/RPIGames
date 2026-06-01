#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "This script must be run with sudo, like so: sudo $0" 
  exit 1
fi
if ! command -v docker &> /dev/null;
  then echo "Docker installation not found. Please install docker." 
  exit 1
fi

./compile_typescript.sh
docker build -t rpi_games_docker_image . -f deploy/dev/docker/Dockerfile
docker container stop rpi_games_docker_container
docker container rm rpi_games_docker_container
docker volume create rpi_games_docker_volume
docker run -d --name rpi_games_docker_container  --mount type=volume,src=rpi_games_docker_volume,dst=/app/db -p 80:80 rpi_games_docker_image
