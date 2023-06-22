#!/bin/bash
docker buildx   build -t $repositiory/debian-py-39:$generation  --platform=$platform ./.. -f debian-py-39  --push=true --output type=registry
docker --log-level "info" buildx build \
      --build-arg REPO_LOCATION=$repositiory \
      --build-arg TAG=$generation \
      --build-arg USER=$user -t \
      $repositiory/xdoc/debian-py-39:$generation  \
      --platform=$platform ./.. -f debian-py-39  --push=true --output type=registry
docker --log-level "info" buildx build \
      --build-arg REPO_LOCATION=$repositiory \
      --build-arg TAG=$generation \
      --build-arg USER=$user -t \
      $repositiory/xdoc/debian-dot-net-core-6-7:$generation  \
      --platform=$platform ./.. -f debian-dot-net-core-6-7  --push=true --output type=registry
docker buildx   build -t $repositiory/debian-dot-net-core-6-7:$generation  --platform=$platform ./.. -f debian-dot-net-core-6-7  --push=true --output type=registry
docker --log-level "info" buildx build \
      --build-arg REPO_LOCATION=$repositiory \
      --build-arg TAG=$generation \
      --build-arg USER=$user -t \
      $repositiory/xdoc/debian-py-39-core:$generation  \
      --platform=$platform ./.. -f debian-py-39-core  --push=true --output type=registry
