#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "This script must be run with sudo, like so: sudo $0" 
  exit 1
fi
if ! command -v docker &> /dev/null;
  then echo "Docker installation not found. Please install docker." 
  exit 1
fi
sudo docker build -t rpi_games_docker_image .
sudo docker container rm rpi_games_docker_container
sudo docker run -d --name rpi_games_docker_container -p 80:80 rpi_games_docker_image
