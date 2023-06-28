#!/bin/bash
docker login https://docker.lacviet.vn -u xdoc -p Lacviet#123
#docker buildx create --use --config /etc/containerd/config.toml
export user=xdoc
export platform_=linux/amd64
export platform=linux/amd64,linux/arm64/v8
export generation_=1
export generation=1
export repositiory=docker.lacviet.vn
export repositiory_=docker.io
export push=docker.lacviet.vn/xdoc
buildFunc(){
# first param is image name
# second param is version
# shellcheck disable=SC1055
#clear
echo "build image $1 from base version $2 to $3"
  docker --log-level "info" buildx build \
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
clear
debian_p=1
#buildFunc 'debian-p' $debian_p
debian_libre_office_headless=1
#buildFunc 'debian-libre-office-headless' $debian_libre_office_headless
debian_dot_net_core=1
#buildFunc 'debian-dot-net-core' $debian_dot_net_core
debian_component=1
#buildFunc 'debian-component' $debian_component
debian_py_core=1
#buildFunc 'debian-py-core' $debian_py_core
debian_py_framework_core=1
#buildFunc 'debian-py-framework-core' $debian_py_core
debian_app_framework=1
#buildFunc 'debian-app-framework'  $debian_app_framework
debian_javac=1
#buildFunc 'debian-javac' $debian_javac
debian_py_torch=$debian_p.1
#buildFunc 'debian-py-torch' $debian_p $debian_py_torch
debian_py_detectron2=1
#buildFunc 'debian-py-detectron2' $debian_py_detectron2
debian_py_torch_vision=1
#buildFunc 'debian-py-torch-vision' $debian_py_torch_vision
debian_py_torch_audio=1
#$buildFunc 'debian-py-torch-audio'  $debian_py_torch_audio
#debian_tika=1
#buildFunc 'debian-tika' $debian_tika
rm -f xdoc-assembly
echo "
  ARG REPO_LOCATION=docker.lacviet.vn
  #FROM $repositiory/$user/debian-p:$debian_p  as python
  FROM $repositiory/$user/debian-libre-office-headless:$debian_libre_office_headless  AS office
  FROM $repositiory/$user/debian-dot-net-core:$debian_dot_net_core  AS dotnet
  FROM $repositiory/$user/debian-component:$debian_component  AS component
  #FROM $repositiory/$user/debian-py-core:$debian_py_core  AS py_core
  #FROM $repositiory/$user/debian-py-framework-core:$debian_py_framework_core as py_framework_core
  #FROM $repositiory/$user/debian-app-framework:$debian_app_framework as debian_app_framework
  FROM $repositiory/$user/debian-javac:$debian_javac as debian_javac
  #FROM $repositiory/$user/debian-py-detectron2:$debian_py_detectron2 as detectron2
  #FROM $repositiory/$user/debian-py-torch-vision:$debian_py_detectron2 as torch_vision
  #FROM $repositiory/$user/debian-py-torch-audio:$debian_py_torch_audio as torch_audio
  FROM debian
  COPY --from=office / /
  COPY --from=dotnet /usr /usr
  COPY --from=component / /
  #COPY --from=python /usr /usr
  #COPY --from=py_framework_core / /
  #COPY --from=py_core / /
  #COPY --from=debian_app_framework / /
  COPY --from=debian_javac / /
  #COPY --from=detectron2 / /
  #COPY --from=torch_vision / /
  #COPY --from=torch_audio / /
  #COPY --from=python /usr/bin/python3 /usr/bin/python3
  #COPY ./../docker-debian/verify.py /docker-debian/verify.py
  #RUN python3 /docker-debian/verify.py --check soffice
  RUN soffice --headless --convert-to png --outdir /tmp /docker-debian/verify.py
  RUN mkdir /python_dot_net_core
  COPY ./../dotnet_core/VietnameseAccent/ ./python_dot_net_core
  RUN dotnet publish ./python_dot_net_core
  #RUN python3  /docker-debian/verify.py check
  COPY ./../docker-debian/verify.png /docker-debian/verify.png
  RUN tesseract /docker-debian/verify.png output --oem 1 -l eng
  #COPY ./../pre_test_build /app/pre_test_build
  #RUN pip install py_vncorenlp
  #RUN python3 /app/pre_test_build/check_py_vncorenlp.py

  #docker buildx   build -t nttlong/test:1  --platform=l$platform ./.. -f debian-xdoc-app  --push=true --output type=registry
" >> xdoc-assembly

xdoc_assembly="$debian_libre_office_headless.$debian_dot_net_core.$debian_component"

#buildFunc 'xdoc-assembly' $xdoc_assembly

rm -f xdoc-py-assembly
xdoc_py_assembly=$debian_py_core.$debian_py_framework_core
echo "
  ARG REPO_LOCATION=docker.lacviet.vn
  FROM $repositiory/$user/debian-p:$debian_p  as python
  FROM $repositiory/$user/debian-py-core:$debian_py_core  as py_core
  FROM $repositiory/$user/debian-py-framework-core:$debian_py_framework_core
  COPY --from=py_core / /
  COPY --from=python / /
  COPY ./../docker-debian/verify.py /docker-debian/verify.py

  RUN pip install py_vncorenlp --no-cache-dir && \
      python3 /docker-debian/verify.py check


  ">> xdoc-py-assembly
#buildFunc 'xdoc-py-assembly' $xdoc_py_assembly
rm -f xdoc-core
echo "

  FROM $repositiory/$user/xdoc-assembly:$xdoc_assembly  as assembly
  FROM $repositiory/$user/xdoc-py-assembly:$xdoc_py_assembly  as py_asm
  FROM $repositiory/$user/debian-p:$debian_p as py
  FROM $repositiory/$user/debian-py-torch:$debian_py_torch
  COPY --from=assembly / /
  COPY --from=py_asm / /
  COPY --from=py / /
  COPY ./../cy_web /app/cy_web
  RUN python3 /app/compact.py /app/cy_web
  ">> xdoc-core
xdoc_core=$debian_p.$xdoc_py_assembly.$xdoc_assembly
#buildFunc 'xdoc-core' $xdoc_core

#debian_java_8=1
#buildFunc 'debian-java-8' $debian_java_8

rm -f xdoc
echo "
  #FROM $repositiory/$user/debian-component:$debian_component as com
#  FROM $repositiory/$user/debian-p:$debian_p as py
  FROM $repositiory/$user/debian-py-torch-vision:$debian_py_torch_vision as torch_vision
  FROM $repositiory/$user/xdoc-core:$xdoc_core

  COPY --from=torch_vision / /

  #COPY --from=py /usr/lib/python3.9/lib-dynload/_lzma.cpython-39-x86_64-linux-gnu.so/ /usr/lib/python3.9/lib-dynload/_lzma.cpython-39-x86_64-linux-gnu.so
  COPY ./../docker-debian/req.txt /app/docker-debian/req.txt
  RUN rm -f /var/lib/dpkg/statoverride
  RUN apt install python-is-python3 -y
  RUN alias python3=python3.9
  RUN python3 -m pip install -r /app/docker-debian/req.txt --no-cache-dir
  COPY ./../cy_utils /app/cy_utils
  COPY ./../cy_xdoc /app/cy_xdoc
  COPY ./../cyx /app/cyx
  COPY ./../cy_consumers /app/cy_consumers
  COPY ./../resource /app/resource
  COPY ./../pre_test_build /app/pre_test_build
  ##COPY ./../docker-debian/verify.py /app/docker-debian/verify.py


#  RUN rm -f /var/lib/dpkg/statoverride
#  RUN apt-get install -y liblzma-dev
#  RUN mkdir -p /usr/local/lib/python3/lib/lib-dynload
#  RUN cp -fr /usr/local/lib/python3.9/lib-dynload /usr/local/lib/python3/lib/lib-dynload
#  RUN python3 /app/docker-debian/verify.py java
  RUN python3 /app/pre_test_build/check_tika_server.py
#  RUN python3 /app/pre_test_build/check_tika_server.py && \
#      python3 /app/pre_test_build/check_torch_version.py
  ">> xdoc
xdoc=$debian_p$xdoc_py_assembly$xdoc_assembly.1
buildFunc 'xdoc' 1 $xdoc