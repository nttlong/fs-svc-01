#!/bin/bash
#-----------------------
# debian-p
#-----------------------
docker_file=debian-p
docker --log-level "info" buildx build \
      --build-arg REPO_LOCATION=$repositiory \
      --build-arg TAG=$generation \
      --build-arg USER=$user -t \
      $push/debian-py-39:$generation  \
      --platform=$platform ./.. -f docker_file  --push=true --output type=registry