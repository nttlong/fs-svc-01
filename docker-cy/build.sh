#!/bin/sh

docker login https://docker.lacviet.vn -u xdoc -p Lacviet#123
#docker buildx create --use --config /etc/containerd/config.toml
export user=xdoc
export user_=nttlong
export platform_=linux/amd64
export platform=linux/amd64,linux/arm64/v8
export repositiory=docker.lacviet.vn
export repositiory_=docker.io
export os='debian'


export top_image=docker.io/python:latest
export top_image=docker.io/python:3.10.12-slim-bookworm
base_py=py310
clear() {
    docker stop $(docker ps -aq)
    docker rm $(docker ps -aq)
    docker rmi $(docker images -q)
    docker volume rm $(docker volume ls)
    docker builder prune -f
    docker system prune -a -f
    docker buildx create --use --config /etc/containerd/config.toml
}
buildFunc(){
# first param is image name
# second param is version
# shellcheck disable=SC1055
#clear


  echo "$repositiory/$user/$1:$2 is checking"
  if [ "-$(docker manifest inspect $repositiory/$user/$1:$2>/dev/nullnull;echo $?)-" = "-0-" ]; then
    echo "$repositiory/$user/$1:$2 is existing"
    return 0
  fi

  #docker  buildx build $repositiory/$user/$1:$2 -t --platform=$platform ./.. -f $1  --push=$3 --output type=registry
  echo "docker  buildx build --build-arg BASE=$3 --build-arg OS_SYS=$4  $repositiory/$user/$1:$2 -t --platform=$platform ./.. -f $1  --push=$3 --output type=registry"
    docker  --log-level "info" buildx build \
          --build-arg BASE=$3 \
          --build-arg OS=$os\
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

#---------------- build libre office------------------------------------
rm -f $base_py-libreoffice && cp -f ./templates/libreoffice ./$base_py-libreoffice
libreoffice_tag=1
libreoffice_image=$base_py-libreoffice:$libreoffice_tag
buildFunc $base_py-libreoffice $libreoffice_tag $top_image $os
#--------------------------------------------------------------------
#---------------- build tessract------------------------------------
rm -f $base_py-tessract && cp -f ./templates/tessract ./$base_py-tessract
tessract_tag=1
tessract_image=$base_py-tessract:$tessract_tag
buildFunc $base_py-tessract $tessract_tag $top_image $os
#--------------------------------------------------------------------
#----------------- build javac ------------------------
rm -f $base_py-javac && cp -f ./templates/javac ./$base_py-javac
javac_tag=1
javac_image=$base_py-javac:$javac_tag
buildFunc $base_py-javac $javac_tag $top_image $os
#--------------------------------------------------------------------
#---------------- build dotnet -----------------------------------------
rm -f $base_py-dotnet && cp -f ./templates/dotnet ./$base_py-dotnet
dotnet_tag=1
dotnet_image=$base_py-dotnet:$dotnet_tag
buildFunc $base_py-dotnet $dotnet_tag $top_image $os
#---------------- build opencv -----------------------------------------
rm -f $base_py-opencv && cp -f ./templates/opencv ./$base_py-opencv
opencv_tag=1
opencv_image=$base_py-opencv:$opencv_tag
buildFunc $base_py-opencv $opencv_tag $top_image $os
#--------------------------------------------------------------------
#---------------- build torch full -----------------------------------------
rm -f $base_py-torch && cp -f ./templates/torch ./$base_py-torch
torch_tag=1
torch_image=$base_py-torch:$torch_tag
#buildFunc $base_py-torch $torch_tag $top_image $os
#---------------- build torch cpu -----------------------------------------
rm -f $base_py-torch-cpu && cp -f ./templates/torch-cpu ./$base_py-torch-cpu
torch_cpu_tag=1
torch_image=$base_py-torch-cpu:$torch_cpu_tag
buildFunc $base_py-torch-cpu $torch_cpu_tag $top_image $os
#---------------- build detectron2 -----------------------------------------
rm -f $base_py-detectron2 && cp -f ./templates/detectron2 ./$base_py-detectron2
detectron2_tag=1
detectron2_image=$base_py-detectron2:$detectron2_tag
@buildFunc $base_py-detectron2 $detectron2_tag $repositiory/$user/$torch_image $os
#---------------- build huggingface -----------------------------------------
rm -f $base_py-huggingface && cp -f ./templates/huggingface ./$base_py-huggingface
huggingface_tag=1
huggingface_image=$base_py-huggingface:$huggingface_tag
buildFunc $base_py-huggingface $huggingface_tag $top_image $os
#---------------- build huggingface -----------------------------------------
rm -f $base_py-deepdoctection && cp -f ./templates/deepdoctection ./$base_py-deepdoctection
deepdoctection_tag=1
deepdoctection_image=$base_py-deepdoctection:$deepdoctection_tag
buildFunc $base_py-deepdoctection $deepdoctection_tag $top_image $os
#--- build cython-build----
rm -f $base_py-cython && cp -f ./templates/cython ./$base_py-cython
cython_tag=1
cython_image=$base_py-cython:$cython_tag
buildFunc $base_py-cython $cython_tag $top_image $os
#--- build fast-client----
rm -f $base_py-fast-client && cp -f ./templates/fast-client ./$base_py-fast-client
fast_client_tag=1
fast_client_image=$base_py-fast-client:$fast_client_tag
buildFunc $base_py-fast-client $fast_client_tag $repositiory/$user/$cython_image $os
#------------ cy_es -------------------
rm -f $base_py-cy_es && cp -f ./templates/cy_es ./$base_py-cy_es
cy_es_tag=1
cy_es_image=$base_py-cy_es:$cy_es_tag
buildFunc $base_py-cy_es $cy_es_tag $repositiory/$user/$cython_image $os
#------------ cy_kit -------------------
rm -f $base_py-cy_kit && cp -f ./templates/cy_kit ./$base_py-cy_kit
cy_kit_tag=1
cy_kit_image=$base_py-cy_kit:$cy_kit_tag
buildFunc $base_py-cy_kit $cy_kit_tag $repositiory/$user/$cython_image $os
#------------ cy_web -------------------
rm -f $base_py-cy_kit && cp -f ./templates/cy_kit ./$base_py-cy_kit
cy_web_tag=1
cy_web_image=$base_py-cy_web:$cy_web_tag
buildFunc $base_py-cy_web $cy_web_tag $repositiory/$user/$cython_image $os
#---------------------combine all components---------------------------
rm -f $base_py-com
echo "
#FROM docker.lacviet.vn/xdoc/py311-libreoffice:1 as office
FROM $repositiory/$user/$libreoffice_image as office
FROM $repositiory/$user/$dotnet_image as dotnet
FROM $repositiory/$user/$tessract_image as tessract
FROM $repositiory/$user/$javac_image as javac
FROM $repositiory/$user/$opencv_image as opencv
FROM $top_image
COPY --from=office / /
COPY --from=dotnet / /
COPY --from=tessract / /
COPY --from=javac / /
COPY --from=opencv / /
RUN mv -f /var/lib/dpkg/statoverride /var/lib/dpkg/statoverride-backup
RUN apt-get update -y && apt-get install -y psmisc nocache
COPY ./../docker-cy/check /check
RUN chmod u+x /check/*.sh
RUN /check/opencv.sh
RUN /check/py_vncorenlp.sh
RUN /check/libreoffice.sh
RUN /check/tessract.sh
RUN /check/tika.sh
RUN /check/dotnet.sh
">>$base_py-com
com=1
export BUILDKIT_PROGRESS=
export platform=linux/amd64,linux/arm64/v8
export platform_=linux/amd64

com_tag=offi$libreoffice_tag.dnet$dotnet_tag.tess$tessract_tag.javc$javac_tag.opcv$opencv_tag.1
com_image=$base_py-com:$com_tag
buildFunc $base_py-com $com_tag $top_image $os
echo "------------deep learning framework----------------"
echo "docker run $repositiory/$user/$detectron2_image"
echo "docker run $repositiory/$user/$huggingface_image"
echo "docker run $repositiory/$user/$deepdoctection_image"
echo "------------------------------------------"
echo "test:"
echo "docker run $repositiory/$user/$com_image /check/libreoffice.sh"
echo "docker run $repositiory/$user/$com_image /check/tessract.sh"
echo "docker run $repositiory/$user/$com_image python3 /check/tika_server.py"
echo "docker run $repositiory/$user/$com_image python3 /check/dotnet.py"
echo "docker run $repositiory/$user/$com_image python3 /check/py_vncorenlp_check.py"
echo "docker run $repositiory/$user/$com_image python3 /check/opencv_check.py"
echo "docker run $repositiory/$user/$com_image python3 -c 'import time;time.sleep(100000000)'"

#docker run docker docker.lacviet.vn/xdoc/py311-deepdoctection:1 python3 -c 'import time;time.sleep(100000000)'
#py3_dotnet=1
#buildFunc $base_py-dotnet $py3_dotnet
#docker buildx create --use --config /etc/containerd/config.toml