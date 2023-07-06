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




rm -f xdoc-asm-os
echo "
#    FROM mcr.microsoft.com/gocv/opencv:4.7.0 AS opencv
    FROM docker.io/python:3.9.5-alpine3.12
#    COPY --from=opencv / /
    RUN apk update && \
        apk add libreoffice && \
        apk add --upgrade tesseract-ocr
    RUN apk add --upgrade ghostscript



">>xdoc-asm-os


rm -f xdoc-asm-py_vncorenlp

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
          cp /usr/lib/jvm/java-1.8-openjdk/jre/lib/aarch64/libjava.so /usr/lib && \
          cp /usr/lib/jvm/java-1.8-openjdk/jre/lib/aarch64/server/libjvm.so /usr/lib &&\
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
#-----------------------------------------
opencv_vserion=3.4.15
rm -f xdoc-lib-cv2
xdoc_lib_cv2=1
echo "
FROM docker.io/python:3.9.5-alpine3.12
RUN apk update && apk upgrade && apk --no-cache add \
  bash \
  build-base \
  ca-certificates \
  clang-dev \
  clang \
  cmake \
  coreutils \
  curl \
  freetype-dev \
  ffmpeg-dev \
  ffmpeg-libs \
  gcc \
  g++ \
  git \
  gettext \
  lcms2-dev \
  libavc1394-dev \
  libc-dev \
  libffi-dev \
  libjpeg-turbo-dev \
  libpng-dev \
  libressl-dev \
  libwebp-dev \
  linux-headers \
  make \
  musl \
  openjpeg-dev \
  openssl \
  python3-dev \
  tiff-dev \
  unzip \
  zlib-dev
#RUN pip install pika
#RUN python3 /app/pre_test_build/check_python_path.py
# Python 3 as default
RUN python3 -m pip install --upgrade pip

# Install NumPy
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h && \
  pip install numpy
# Install OpenCV
RUN mkdir -p /opt
RUN wget -O /opt/$opencv_vserion.zip https://github.com/opencv/opencv/archive/$opencv_vserion.zip
RUN wget -O /opt/opencv_contrib-$opencv_vserion.zip https://github.com/opencv/opencv_contrib/archive/$opencv_vserion.zip
RUN cd /opt && unzip $opencv_vserion.zip
RUN cd /opt && unzip opencv_contrib-$opencv_vserion.zip
#RUN ls  /opt/opencv-$opencv_vserion; exit 1
#RUN mkdir -p /opt/opencv-$opencv_vserion/build
RUN apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/v3.14/main  ca-certificates
RUN apk add openjpeg
RUN  cd /opt/opencv-$opencv_vserion && mkdir build && cd build && cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_C_COMPILER=/usr/bin/clang \
    -D CMAKE_CXX_COMPILER=/usr/bin/clang++ \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D INSTALL_C_EXAMPLES=OFF \
    -D WITH_FFMPEG=ON \
    -D WITH_TBB=ON \
    -D OPENCV_EXTRA_MODULES_PATH=/opt/opencv_contrib-$opencv_vserion/modules \
    -D PYTHON_EXECUTABLE=/usr/local/bin/python3 \
    .. \
  && \
  make -j\$(nproc) && make install && cd .. && rm -rf build

  RUN cp -p \$(find /usr/local/lib/python3.9/site-packages -name cv2.*.so) \
   /usr/local/lib/python3.9/site-packages/cv2.so && \
   python -c 'import cv2; print(\"Python: import cv2 - SUCCESS\")'
   RUN rm -f /opt && unzip opencv_contrib-$opencv_vserion.zip && \
        rm -f /opt && unzip $opencv_vserion.zip
">>xdoc-lib-cv2

#-------------------------------------------------------------------------
rm -f alpine312-py395-lib-torch
cp torch alpine312-py395-lib-torch
#---------------------------------------------------------------------
rm -f xdoc-slim
xdoc_asm_os=1
xdoc_asm_lv_accent_huy=1
xdoc_asm_api_req=1
xdoc_asm_py_vncorenlp=1
alpine312_py395_lib_torch_arm190_amd201_cpu=1
echo "
      FROM $repositiory/$user/xdoc-asm-api-req:$xdoc_asm_api_req as req
      FROM $repositiory/$user/xdoc-asm-lv-accent-huy:$xdoc_asm_lv_accent_huy as lv
      FROM $repositiory/$user/xdoc-asm-py_vncorenlp:$xdoc_asm_py_vncorenlp as vncorenlp
      FROM $repositiory/$user/xdoc-asm-os:$xdoc_asm_os as os
      FROM $repositiory/$user/xdoc-lib-cv2:$xdoc_lib_cv2 as cv2

      FROM docker.io/python:3.9.5-alpine3.12
      ARG TARGETARCH
      RUN apk update && apk upgrade
      COPY --from=req / /
      COPY --from=lv / /
      COPY --from=vncorenlp / /
      COPY --from=os / /
      COPY --from=cv2 / /

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
      COPY ./../docker-asm/check_os.py /app/check_os.py
      RUN cp /usr/lib/jvm/java-1.8-openjdk/jre/lib/aarch64/libjava.so /usr/lib/jvm/java-1.8-openjdk/bin; exit 0
      RUN cp /usr/lib/jvm/java-1.8-openjdk/jre/lib/aarch64/server/libjvm.so /usr/lib/jvm/java-1.8-openjdk/jre/lib/aarch64; exit 0
      RUN python3 /app/pre_test_build/check_py_vncorenlp.py
      RUN killall python; exit 0
      RUN killall java; exit 0
      RUN python3 /app/pre_test_build/check_open_cv.py
      RUN python3 /app/pre_test_build/check_tika_server.py
      RUN python3 -c 'import torch; print(torch.__file__)'; exit 1
">> xdoc-slim
export platform_=linux/amd64,linux/arm64/v8
export platform=linux/arm64/v8
export platform__=linux/amd64
release_name=rc

#buildFunc xdoc-asm-os $xdoc_asm_os $is_publish

#buildFunc xdoc-asm-lv-accent-huy $xdoc_asm_lv_accent_huy $is_publish

#buildFunc xdoc-asm-api-req $xdoc_asm_api_req $is_publish

export BUILDKIT_PROGRESS=
#buildFunc xdoc-asm-py_vncorenlp $xdoc_asm_py_vncorenlp $is_publish

#buildFunc "xdoc-lib-cv2" $xdoc_lib_cv2 False

buildFunc torch alpine312-py395-lib-torch $alpine312_py395_lib_torch_arm190_amd201_cpu $is_publish
xdoc_asm_slim=$xdoc_asm_os.$xdoc_asm_py_vncorenlp.$xdoc_asm_lv_accent_huy.$xdoc_asm_api_req.15
#buildFunc xdoc-slim $xdoc_asm_slim $is_publish
echo "docker run -p 8012:8012 $repositiory/$user/xdoc-slim:$xdoc_asm_slim python3 /app/cy_xdoc/server.py"
#docker buildx create --use --config /etc/containerd/config.toml