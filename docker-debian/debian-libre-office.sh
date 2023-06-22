#!/bin/bash
#debian-libre-office
docker_file=debian-libre-office
docker --log-level "info" buildx build \
      --build-arg REPO_LOCATION=$repositiory \
      --build-arg TAG=$generation \
      --build-arg USER=$user -t \
      $push/$docker_file:$generation  \
      --platform=$platform ./.. -f $docker_file  --push=true --output type=registry