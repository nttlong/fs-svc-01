#!/bin/sh
export version='rc.0.5.3.1'
export platform='linux/amd64,linux/arm64/v8'
docker buildx   build -t nttlong/files-service-final:$version  --platform=$platform  ./.. -f files-service-final  --push=true --output type=registry
