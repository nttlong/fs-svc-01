#!/bin/sh
export test_version='rc.0.5.3.0.amd.aws1'
export test_platform='linux/amd64'
export platform='linux/amd64,linux/arm64/v8'

export version='rc.0.5.3.1'
docker buildx   build -t nttlong/files-service-final:$test_version  --platform=$test_platform  ./.. -f files-service-final  --push=true --output type=registry
