#!/bin/bash
docker buildx create --use --config /etc/containerd/config.toml
platform=linux/amd64
generation=adm.1
muli_platform=linux/amd64,linux/arm64/v8
repositiory=docker.lacviet.vn/xdoc
docker buildx   build -t $repositiory/debian-py-39:$generation  --platform=$platform ./.. -f debian-py-39  --push=true --output type=registry