#!/bin/bash
docker login https://docker.lacviet.vn -u xdoc -p Lacviet#123
#docker buildx create --use --config /etc/containerd/config.toml
export user=xdoc
export platform_=linux/arm64
export platform=linux/amd64,linux/arm64/v8
export repositiory=docker.lacviet.vn
export repositiory_=docker.io
export push=docker.lacviet.vn/xdoc
export BUILDKIT_PROGRESS=plain
buildFunc(){
# first param is image name
# second param is version
# shellcheck disable=SC1055
#clear

echo "build image $1 from base version $2 to $3"
  docker  --log-level "info" buildx build \
        --build-arg REPO_LOCATION=$repositiory \
        --build-arg TAG="$2" \
        --build-arg USER=$user -t \
        $repositiory/$user/$1:$3  \
        --platform=$platform ./.. -f $1  --push=true --output type=registry
  exit_status=$?
  if [ ${exit_status} -ne 0 ]; then
    echo "build image $1 from base version $2 to $3 error"
    exit "${exit_status}"
  fi
}
stage1=rc.1
rm -f "stage-1"
echo "
  FROM docker.io/nttlong/base-core-slim-req:rc.2023.002
  ARG TARGETARCH
  RUN apt-get update && apt-get install -y lsb-release && apt-get clean all
  COPY ./../docker-debian/verify.py /app/docker-debian/verify.py
  RUN python3 /app/docker-debian/verify.py check
  COPY ./../compact.py /app/compact.py
  RUN  pip install Cython==3.0.0b1 && pip uninstall -y pymongo
  COPY ./../docker-resource/jdk-8u361-linux-aarch64.rpm /tmp/jdk-8u361-linux-aarch64.rpm
  RUN if [ \"\$TARGETARCH\" = \"arm64\" ]; then \
      cd /tmp;\
      apt-get install alien -y;\
      rpm -i jdk-8u361-linux-aarch64.rpm;\
      alien jdk-8u361-linux-aarch64.rpm;\
      dpkg –i jdk-8u361-linux-aarch64.deb;\
      fi
">>stage-1
#buildFunc "stage-1" 1 $stage1
#-----------------------------------------------
stage2=$stage1.1
rm -f "stage-2"
echo "
  FROM $repositiory/$user/stage-1:$stage1
  ARG TARGETARCH
  RUN apt-get update && apt-get install -y lsb-release && apt-get clean all
  COPY ./../docker-debian/verify.py /app/docker-debian/verify.py
  RUN pip install Cython==3.0.0b1 && python3 /app/docker-debian/verify.py check
  COPY ./../compact.py /app/compact.py
  COPY ./../pymongo /app/bson
  COPY ./../gridfs /app/gridfs
  COPY ./../pymongo /app/pymongo
  COPY ./../elasticsearch /app/elasticsearch
  COPY ./../build /app/build
  RUN pip install pymongo
  RUN if [ \"\$TARGETARCH\" = \"amd64\" ]; then \
       rm -fr  /usr/local/lib/python3.9/dist-packages/pymongo;\
       rm -fr /usr/local/lib/python3.9/dist-packages/elasticsearch;\
       rm -fr /usr/local/lib/python3.9/dist-packages/gridfs;\
      python3 /app/docker-debian/verify.py py39_core ;\
      fi
  RUN if [ \"\$TARGETARCH\" = \"arm64\" ]; then \
       rm -fr /app/bson;\
       rm -fr /app/gridfs;\
       rm -fr /app/elasticsearch;\
       rm -fr /app/build;\
       pip install elasticsearch && pip install pymongo;\
      fi
">>stage-2
#buildFunc "stage-2" 1 $stage2
#----------------------------------------------
stage3=$stage2.1
rm -f "stage-3"
echo "

  FROM $repositiory/$user/stage-2:$stage2
  ARG TARGETARCH
  RUN apt-get update && apt-get install -y lsb-release && apt-get clean all
  COPY ./../docker-debian/verify.py /app/docker-debian/verify.py
  RUN pip install Cython==3.0.0b1 && python3 /app/docker-debian/verify.py check
  COPY ./../compact.py /app/compact.py
  COPY ./../cy_docs /app/cy_docs
  COPY ./../cy_es /app/cy_es
  COPY ./../cy_kit /app/cy_kit
  COPY ./../cy_web /app/cy_web
  COPY ./../build /app/build

  RUN if [ \"\$TARGETARCH\" = \"\amd64\" ]; then \
      python3 /app/docker-debian/verify1.py py39_core core_framework ;\
      fi
  RUN if [ \"\$TARGETARCH\" = \"arm64\" ]; then \
       rm -fr /app/build;\
      fi


">>stage-3
#buildFunc "stage-3" 1 $stage3
#--------------------------------------
xdoc_tika=2
rm -f "xdoc-tika-server"
echo "
    FROM docker.io/iwishiwasaneagle/apache-tika-arm:latest
">>"xdoc-tika-server"
#buildFunc "xdoc-tika-server" 1 1
#---------------------------------------------------
xdoc=$stage3.3
rm -f "xdoc"
echo "
  FROM $repositiory/$user/stage-3:$stage3
  ARG TARGETARCH
  COPY ./../docker-debian/xdoc.req.txt /app/xdoc.req.txt
  RUN pip install -r /app/xdoc.req.txt --no-cache-dir
  COPY ./../cy_xdoc /app/cy_xdoc
  COPY ./../cyx /app/cyx
  COPY ./../cy_consumers /app/cy_consumers
  COPY ./../pre_test_build /app/pre_test_build
  COPY ./../docker-debian/verify.py /docker-debian/verify.py
  RUN python3 /docker-debian/verify.py --check soffice
  RUN soffice --headless --convert-to png --outdir /tmp /docker-debian/verify.py
  COPY ./../config.yml /app/config.yml
  COPY ./../resource /app/resource
  COPY ./../docker-debian/verify.png /docker-debian/verify.png
  RUN tesseract /docker-debian/verify.png output --oem 1 -l eng
  RUN python3 /app/pre_test_build/check_tika_server.py
  RUN python3 /app/pre_test_build/check_py_vncorenlp.py
  RUN python3 /app/pre_test_build/check_vn_predict.py

">>xdoc
buildFunc "xdoc" 1 $xdoc
echo "Build complete"
echo "----------------------------------------"
echo  "Test:"
echo "docker run  -p 8012:8014 $repositiory/$user/xdoc:$xdoc python3 /app/cy_xdoc/server.py"
