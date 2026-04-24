#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "This script must be run with sudo, like so: sudo $0" 
  exit 1
fi
if ! command -v docker &> /dev/null;
  then echo "Docker installation not found. Please install docker." 
  exit 1
fi
docker container logs rpi_games_docker_container