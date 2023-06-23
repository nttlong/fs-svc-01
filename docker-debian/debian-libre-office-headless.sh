#!/bin/bash
export user=xdoc
export platform_=linux/amd64
export platform=linux/amd64,linux/arm64/v8
export generation=adm.1
export generation=1
export repositiory=docker.lacviet.vn
export push=docker.lacviet.vn/xdoc
docker_file=debian-libre-office-headless
docker --log-level "info" buildx build \
      --build-arg REPO_LOCATION=$repositiory \
      --build-arg TAG="$1" \
      --build-arg USER=$user -t \
      $push/$docker_file:$generation  \
      --platform=$platform ./.. -f $docker_file  --push=true --output type=registry