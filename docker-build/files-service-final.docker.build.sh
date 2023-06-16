#!/bin/sh
export version='rc.0.5.3.0amd17'
docker buildx   build -t nttlong/files-service-final:$version  --platform=linux/amd64  ./.. -f files-service-final  --push=true --output type=registry
