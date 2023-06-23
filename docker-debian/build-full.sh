#!/bin/bash
docker login https://docker.lacviet.vn -u xdoc -p Lacviet#123
#docker buildx create --use --config /etc/containerd/config.toml
export user=xdoc
export platform_=linux/amd64
export platform=linux/amd64,linux/arm64/v8
export generation_=adm.1
export generation=1
export repositiory=docker.lacviet.vn
export push=docker.lacviet.vn/xdoc
buildFunc(){
# first param is image name
# second param is version
# shellcheck disable=SC1055
echo "build image $1 version $2"
  docker --log-level "info" buildx build \
        --build-arg REPO_LOCATION=$repositiory \
        --build-arg TAG="$2" \
        --build-arg USER=$user -t \
        $repositiory/$user/$1:$2  \
        --platform=$platform ./.. -f $1  --push=true --output type=registry
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
release=1
rm -f debian-xdoc-app
echo "
  ARG REPO_LOCATION=docker.lacviet.vn
  FROM $repositiory/$user/debian-p:$debian_p  as python
  FROM $repositiory/$user/debian-libre-office-headless:$debian_libre_office_headless  AS office
  FROM $repositiory/$user/debian-dot-net-core:$debian_dot_net_core  AS dotnet
  FROM $repositiory/$user/debian-component:$debian_component  AS component
  FROM $repositiory/$user/debian-py-core:$debian_py_core  AS py_core
  FROM $repositiory/$user/debian-py-framework-core:$debian_py_framework_core as py_framework_core
  FROM debian
  COPY --from=office / /
  COPY --from=dotnet /usr /usr
  COPY --from=component / /
  COPY --from=python /usr /usr
  COPY --from=py_framework_core / /
  COPY --from=py_core / /

  #COPY --from=python /usr/bin/python3 /usr/bin/python3
  COPY ./../docker-debian/verify.py /docker-debian/verify.py
  RUN python3 /docker-debian/verify.py --check soffice
  RUN soffice --headless --convert-to png --outdir /tmp /docker-debian/verify.py
  RUN mkdir /python_dot_net_core
  COPY ./../dotnet_core/VietnameseAccent/ ./python_dot_net_core
  RUN dotnet publish ./python_dot_net_core
  RUN python3  /docker-debian/verify.py check
  COPY ./../docker-debian/verify.png /docker-debian/verify.png
  RUN tesseract /docker-debian/verify.png output --oem 1 -l eng

  #docker buildx   build -t nttlong/test:1  --platform=l$platform ./.. -f debian-xdoc-app  --push=true --output type=registry
" >> debian-xdoc-app

buildFunc 'debian-xdoc-app' "$debian_p.$debian_libre_office_headless.$debian_dot_net_core.$debian_component.$debian_py_core.$debian_py_framework_core.$release"