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

buildFunc(){
# first param is image name
# second param is version
# shellcheck disable=SC1055
#clear

echo "docker  buildx build --build-arg BASE=$3 --build-arg OS_SYS=$4  $repositiory/$user/$1:$2 -t --platform=$platform ./.. -f $1  --push=$3 --output type=registry"
  #docker  buildx build $repositiory/$user/$1:$2 -t --platform=$platform ./.. -f $1  --push=$3 --output type=registry
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
base_py=py311
#---------------- build libre office------------------------------------
rm -f $base_py-libreoffice && cp -f ./templates/libreoffice ./$base_py-libreoffice
libreoffice_tag=1
libreoffice_image=$base_py-libreoffice:$libreoffice_tag
#buildFunc $base_py-libreoffice $libreoffice_tag $top_image
#--------------------------------------------------------------------
#---------------- build tessract------------------------------------
rm -f $base_py-tessract && cp -f ./templates/tessract ./$base_py-tessract
tessract_tag=1
tessract_image=$base_py-tessract:$tessract_tag
#buildFunc $base_py-tessract $tessract_tag $top_image
#--------------------------------------------------------------------
#----------------- build javac ------------------------
rm -f $base_py-javac && cp -f ./templates/javac ./$base_py-javac
javac_tag=1
javac_image=$base_py-javac:$javac_tag
#buildFunc $base_py-javac $javac_tag $top_image
#--------------------------------------------------------------------
#---------------- build dotnet -----------------------------------------
rm -f $base_py-dotnet && cp -f ./templates/dotnet ./$base_py-dotnet
dotnet_tag=3
dotnet_image=$base_py-dotnet:$dotnet_tag
#buildFunc $base_py-dotnet $dotnet_tag $top_image $os
#---------------- build opencv -----------------------------------------
rm -f $base_py-opencv && cp -f ./templates/opencv ./$base_py-opencv
opencv_tag=1
opencv_image=$base_py-opencv:$opencv_tag
#buildFunc $base_py-opencv $opencv_tag $top_image $os
#--------------------------------------------------------------------
#---------------- build opencv -----------------------------------------
rm -f $base_py-torch && cp -f ./templates/torch ./$base_py-torch
torch_tag=1
torch_image=$base_py-torch:$torch_tag
buildFunc $base_py-torch $torch_tag $top_image $os
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
#buildFunc $base_py-com $com_tag $top_image $os
echo "------------------------------------------"
echo "test:"
echo "docker run $repositiory/$user/$com_image /check/libreoffice.sh"
echo "docker run $repositiory/$user/$com_image /check/tessract.sh"
echo "docker run $repositiory/$user/$com_image python3 /check/tika_server.py"
echo "docker run $repositiory/$user/$com_image python3 /check/dotnet.py"
echo "docker run $repositiory/$user/$com_image python3 /check/py_vncorenlp_check.py"
echo "docker run $repositiory/$user/$com_image python3 /check/opencv_check.py"
echo "docker run $repositiory/$user/$com_image python3 -c 'import time;time.sleep(100000000)'"
#py3_dotnet=1
#buildFunc $base_py-dotnet $py3_dotnet
#docker buildx create --use --config /etc/containerd/config.toml