#!/bin/bash
docker login https://docker.lacviet.vn -u xdoc -p Lacviet#123
#docker buildx create --use --config /etc/containerd/config.toml
export user=xdoc
export user_=nttlong
export platform=linux/amd64
export platform_=linux/amd64,linux/arm64/v8
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



xdoc_asm_os=3
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
    RUN apk --no-cache add gcc musl-dev linux-headers g++ libffi libffi-dev
    RUN python -m pip install --upgrade pip
     RUN pip install pythonnet==3.0.1

">>xdoc-asm-os


rm -f xdoc-asm-py_vncorenlp
xdoc_asm_py_vncorenlp=1
echo "
      FROM docker.io/python:3.9.5-alpine3.12
      ARG TARGETARCH
      RUN apk update && apk upgrade && apk fetch openjdk8 && apk add openjdk8
      RUN apk --no-cache add gcc musl-dev linux-headers g++ libffi libffi-dev
      RUN python3 -m pip install --upgrade pip
      ENV JAVA_HOME=/usr/lib/jvm/java-1.8-openjdk
      ENV PATH=\"\$JAVA_HOME/bin:\${PATH}\"
      RUN pip install py-vncorenlp
      COPY ./../cyx /app/cyx
      COPY ./../pre_test_build /app/pre_test_build
      COPY ./../docker-asm/check_os.py /app/check_os.py
     RUN  if [ \"\$TARGETARCH\" = \"amd64\" ]; then \
          cp /usr/lib/jvm/java-1.8-openjdk/jre/lib/amd64/libjava.so /usr/lib && \
          cp /usr/lib/jvm/java-1.8-openjdk/jre/lib/amd64/server/libjvm.so /usr/lib && \
          python3 /app/pre_test_build/check_py_vncorenlp.py;\
          fi
     RUN if [\"\$TARGETARCH\"=\"arm64\"]; then \
          cp /usr/lib/jvm/java-1.8-openjdk/jre/lib/arm64/libjava.so /usr/lib && \
          cp /usr/lib/jvm/java-1.8-openjdk/jre/lib/arm64/server/libjvm.so /usr/lib &&\
          python3 /app/pre_test_build/check_py_vncorenlp.py;\
          fi
#     RUN python3 /app/pre_test_build/check_py_vncorenlp.py
">>xdoc-asm-py_vncorenlp

#-------------------------------------------------------------
rm -f xdoc-asm-lv-accent-huy
echo "
    FROM mcr.microsoft.com/dotnet/sdk:6.0-alpine AS donet
    FROM docker.io/python:3.9.5-alpine3.12
    COPY --from=donet / /
    RUN mkdir /python_dot_net_core
    COPY ./../dotnet_core/VietnameseAccent/ ./python_dot_net_core
    RUN dotnet publish ./python_dot_net_core
    RUN apk --no-cache add gcc musl-dev linux-headers g++ libffi libffi-dev
    RUN python -m pip install --upgrade pip
    RUN pip install pythonnet==3.0.1
">>xdoc-asm-lv-accent-huy

rm -f xdoc-asm-api-req
echo "
      FROM docker.io/python:3.9.5-alpine3.12
      COPY ./../docker-asm/check_os.py /tmp/docker-asm/check_os.py
      COPY ./../docker-asm/req.txt /tmp/docker-asm/req.txt
      RUN apk --no-cache add gcc musl-dev linux-headers g++ libffi libffi-dev && \
          python -m pip install --upgrade pip && \
          pip install -r /tmp/docker-asm/req.txt
      RUN rm -rf /root/.cache/pip
">>xdoc-asm-api-req
xdoc_asm_api_req=$release_name.0


xdoc_asm_lv_accent_huy=1

rm -f xdoc-slim

echo "
      FROM $repositiory/$user/xdoc-asm-api-req:$xdoc_asm_api_req as req
      FROM $repositiory/$user/xdoc-asm-lv-accent-huy:$xdoc_asm_lv_accent_huy as lv
      FROM $repositiory/$user/xdoc-asm-py_vncorenlp:$xdoc_asm_py_vncorenlp as vncorenlp
      FROM docker.io/python:3.9.5-alpine3.12
      ARG TARGETARCH
      COPY --from=req / /
      COPY --from=lv / /
      COPY --from=vncorenlp / /
      COPY ./../cy_docs /app/cy_docs
      COPY ./../cy_es /app/cy_es
      COPY ./../cyx /app/cyx
      COPY ./../cy_kit /app/cy_kit
      COPY ./../cy_utils /app/cy_utils
      COPY ./../cy_web /app/cy_web
      COPY ./../cy_xdoc /app/cy_xdoc
      COPY ./../config.yml /app/config.yml
      COPY ./../resource /app/resource
      COPY ./../pre_test_build /app/pre_test_build
      ENV JAVA_HOME=/usr/lib/jvm/java-1.8-openjdk
      ENV PATH=\"\$JAVA_HOME/bin:\${PATH}\"
#      RUN pip uninstall elasticsearch -y && pip install elasticsearch==6.8.2
      RUN python3 /app/pre_test_build/check_py_vncorenlp.py;
">> xdoc-slim
export platform=linux/amd64,linux/arm64/v8
release_name=rc
xdoc_asm_os=$release_name.1
#buildFunc xdoc-asm-os $xdoc_asm_os $is_publish
xdoc_asm_lv_accent_huy=1
#buildFunc xdoc-asm-lv-accent-huy $xdoc_asm_lv_accent_huy $is_publish
xdoc_asm_api_req=1
#buildFunc xdoc-asm-api-req $xdoc_asm_api_req $is_publish
xdoc_asm_py_vncorenlp=1
export BUILDKIT_PROGRESS=
buildFunc xdoc-asm-py_vncorenlp $xdoc_asm_py_vncorenlp $is_publish
xdoc_asm_slim=$xdoc_asm_os.$xdoc_asm_py_vncorenlp.$xdoc_asm_lv_accent_huy.$xdoc_asm_api_req.15
buildFunc xdoc-slim $xdoc_asm_slim $is_publish
echo "docker run -p 8012:8012 $repositiory/$user/xdoc-asm-test:$xdoc_asm_test python3 /app/cy_xdoc/server.py"
