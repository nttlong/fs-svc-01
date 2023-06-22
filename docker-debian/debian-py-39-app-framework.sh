#!/bin/bash
##--------------------------
# debian-py-39-app-framework
#------------------------------
docker_file=debian-py-39-app-framework
docker --log-level "info" buildx build \
      --build-arg REPO_LOCATION=$repositiory \
      --build-arg TAG=$generation \
      --build-arg USER=$user -t \
      $push/$docker_file:$generation  \
      --platform=$platform ./.. -f $docker_file  --push=true --output type=registry