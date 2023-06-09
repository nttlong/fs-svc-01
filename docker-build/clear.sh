#!/bin/sh
docker stop $(docker ps -aq)

docker rm $(docker ps -aq)
docker rmi $(docker images -q)
docker volume rm $(docker volume ls)
docker system prune -a