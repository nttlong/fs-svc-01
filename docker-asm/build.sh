#!/bin/bash
docker login https://docker.lacviet.vn -u xdoc -p Lacviet#123
#docker buildx create --use --config /etc/containerd/config.toml
export user=xdoc
export user_=nttlong
export platform_=linux/amd64
export platform=linux/amd64,linux/arm64/v8
export repositiory=docker.lacviet.vn
export repositiory_=docker.io
export push=docker.lacviet.vn/xdoc
#export BUILDKIT_PROGRESS=plain
export release_name=amd
buildFunc(){
# first param is image name
# second param is version
# shellcheck disable=SC1055
#clear

echo "docker  buildx build $repositiory/$user/$1:$2 -t --platform=$platform ./.. -f $1  --push=$3 --output type=registry"
  #docker  buildx build $repositiory/$user/$1:$2 -t --platform=$platform ./.. -f $1  --push=$3 --output type=registry
  docker  --log-level "info" buildx build \
        -t \
        $repositiory/$user/$1:$2  \
        --platform=$platform ./.. -f $1  --push=true --output type=registry
  exit_status=$?
  if [ ${exit_status} -ne 0 ]; then
    echo "build image $1 from base version $2 to $3 error"
    exit "${exit_status}"
  fi
  exit_status=$?
  if [ ${exit_status} -ne 0 ]; then
    echo "build image $1 from base version $2 to $3 error"
    exit "${exit_status}"
  fi
}
is_publish=True
release_name="amd"



xdoc_asm_office=2
rm -f xdoc-asm-os
echo "
    FROM mcr.microsoft.com/dotnet/sdk:6.0-alpine AS donet
    FROM docker.io/python:3.9.5-alpine3.12
    COPY --from=donet / /
    RUN apk update && \
        apk add libreoffice && \
        apk add --upgrade tesseract-ocr

    RUN apk fetch openjdk8 && apk add openjdk8
    ENV JAVA_HOME=/usr/lib/jvm/java-1.8-openjdk
    ENV PATH=\"\$JAVA_HOME/bin:\${PATH}\"
    COPY ./../docker-asm/check_os.py /tmp/docker-asm/check_os.py
    RUN soffice --headless --convert-to png --outdir /tmp /tmp/docker-asm/check_os.py
    RUN tesseract /tmp/check_os.png output --oem 1 -l eng
    RUN mkdir /python_dot_net_core
    COPY ./../dotnet_core/VietnameseAccent/ ./python_dot_net_core
    RUN dotnet publish ./python_dot_net_core

">>xdoc-asm-office
xdoc_asm_office=0
buildFunc xdoc-asm-office $xdoc_asm_office true
rm -f xdoc-asm-core
echo "
      FROM docker.io/python:3.9.5-alpine3.12
      RUN apk update && apk upgrade
      RUN apk --no-cache add musl-dev linux-headers g++
      COPY ./../docker-asm/check_os.py /tmp/docker-asm/check_os.py
      COPY ./../docker-asm/req.txt /tmp/docker-asm/req.txt
      RUN pip install -r /tmp/docker-asm/req.txt --no-cache-dir

">>xdoc-asm-0
xdoc_asm_0=$release_name.0

buildFunc xdoc-asm-0 $xdoc_asm_0 $is_publish