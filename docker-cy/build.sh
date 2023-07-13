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
reset_build() {
    docker stop $(docker ps -aq)
    docker rm $(docker ps -aq)
    docker rmi $(docker images -q)
    docker volume rm $(docker volume ls)
    docker builder prune -f
    docker system prune -a -f
    docker buildx create --use --config /etc/containerd/config.toml

}
tag(){
  if [ "$platform" = "linux/amd64,linux/arm64/v8" ]; then
    echo "$1"
  fi
  if [ "$platform" = "linux/amd64" ]; then
    echo "adm.$1"
  fi
  if [ "$platform" = "linux/arm64/v8" ]; then
    echo "arm.$1"
  fi
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
    if [ "-$exit_status-" = "-0-" ]; then
      reset_build
    fi
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
libreoffice_tag_build=$(tag $libreoffice_tag)
libreoffice_image=$base_py-libreoffice:$libreoffice_tag_build
buildFunc $base_py-libreoffice $libreoffice_tag_build $top_image $os
#--------------------------------------------------------------------
#---------------- build tessract------------------------------------
rm -f $base_py-tessract && cp -f ./templates/tessract ./$base_py-tessract
tessract_tag=1
tessract_tag_build=$(tag $tessract_tag)
tessract_image=$base_py-tessract:$tessract_tag_build
buildFunc $base_py-tessract $tessract_tag_build $top_image $os
#--------------------------------------------------------------------
#----------------- build javac ------------------------
rm -f $base_py-javac && cp -f ./templates/javac ./$base_py-javac
javac_tag=1
javac_tag_build=$(tag $javac_tag)
javac_image=$base_py-javac:$javac_tag_build
buildFunc $base_py-javac $javac_tag_build $top_image $os
#--------------------------------------------------------------------
#---------------- build dotnet -----------------------------------------
rm -f $base_py-dotnet && cp -f ./templates/dotnet ./$base_py-dotnet
dotnet_tag=1
dotnet_tag_build=$(tag $dotnet_tag)

dotnet_image=$base_py-dotnet:$dotnet_tag_build
buildFunc $base_py-dotnet $dotnet_tag_build $top_image $os
#---------------- build opencv -----------------------------------------
rm -f $base_py-opencv && cp -f ./templates/opencv ./$base_py-opencv
opencv_tag=2
opencv_tag_build=$(tag $opencv_tag)
opencv_image=$base_py-opencv:$opencv_tag_build
buildFunc $base_py-opencv $opencv_tag_build $top_image $os
#--------------------------------------------------------------------
#---------------- build torch full -----------------------------------------
rm -f $base_py-torch && cp -f ./templates/torch ./$base_py-torch
torch_tag=1
torch_tag_build=$(tag $torch_tag)
torch_image=$base_py-torch:$torch_tag_build
#buildFunc $base_py-torch $torch_tag $top_image $os
#---------------- build torch cpu -----------------------------------------
rm -f $base_py-torch-cpu && cp -f ./templates/torch-cpu ./$base_py-torch-cpu
torch_cpu_tag=1
torch_cpu_tag_build=$(tag $torch_cpu_tag)
torch_image=$base_py-torch-cpu:$torch_cpu_tag_build
buildFunc $base_py-torch-cpu $torch_cpu_tag_build $top_image $os
#---------------- build detectron2 -----------------------------------------
rm -f $base_py-detectron2 && cp -f ./templates/detectron2 ./$base_py-detectron2
detectron2_tag=1
detectron2_tag_build=$(tag $detectron2_tag)
detectron2_image=$base_py-detectron2:$detectron2_tag_build
buildFunc $base_py-detectron2 $detectron2_tag_build $repositiory/$user/$torch_image $os
#---------------- build huggingface -----------------------------------------
rm -f $base_py-huggingface && cp -f ./templates/huggingface ./$base_py-huggingface
huggingface_tag=1
huggingface_tag_build=$(tag $huggingface_tag)
huggingface_image=$base_py-huggingface:$huggingface_tag_build
buildFunc $base_py-huggingface $huggingface_tag_build $top_image $os
#---------------- build huggingface -----------------------------------------
rm -f $base_py-deepdoctection && cp -f ./templates/deepdoctection ./$base_py-deepdoctection
deepdoctection_tag=2
deepdoctection_tag_build=$(tag $deepdoctection_tag)
deepdoctection_image=$base_py-deepdoctection:$deepdoctection_tag_build
buildFunc $base_py-deepdoctection $deepdoctection_tag_build $top_image $os
#----------- build deep-learning-----------
rm -f $base_py-deep-learning
echo "
FROM $repositiory/$user/$torch_image as torch
FROM $repositiory/$user/$detectron2_image as detectron2
FROM $repositiory/$user/$huggingface_image as huggingface
FROM $repositiory/$user/$deepdoctection_image as deepdoctection
FROM $top_image
COPY --from=torch / /
COPY --from=detectron2 / /
COPY --from=huggingface / /
COPY --from=deepdoctection / /

">>$base_py-deep-learning
deep_learning_tag=$(($torch_cpu_tag+$detectron2_tag+$huggingface_tag+$deepdoctection_tag))
deep_learning_tag_build=$(tag $deep_learning_tag)
deep_learning_image=$base_py-deep-learning:$deep_learning_tag_build
buildFunc $base_py-deep-learning $deep_learning_tag_build $os
#--- build cython-build----
rm -f $base_py-cython && cp -f ./templates/cython ./$base_py-cython
cython_tag=1
cython_tag_build=$(tag $cython_tag)
cython_image=$base_py-cython:$cython_tag_build
buildFunc $base_py-cython $cython_tag_build $top_image $os
#--- build fast-client----
rm -f $base_py-fast-client && cp -f ./templates/fast-client ./$base_py-fast-client
fast_client_tag=1
fast_client_tag_build=$(tag $fast_client_tag)
fast_client_image=$base_py-fast-client:$fast_client_tag_build
buildFunc $base_py-fast-client $fast_client_tag_build $repositiory/$user/$cython_image $os
#------------ cy_es -------------------
rm -f $base_py-cy_es && cp -f ./templates/cy_es ./$base_py-cy_es
cy_es_tag=1
cy_es_tag_build=$(tag $cy_es_tag)
cy_es_image=$base_py-cy_es:$cy_es_tag_build
buildFunc $base_py-cy_es $cy_es_tag_build $repositiory/$user/$cython_image $os
#------------ cy_kit -------------------
rm -f $base_py-cy_kit && cp -f ./templates/cy_kit ./$base_py-cy_kit
cy_kit_tag=1
cy_kit_tag_build=$(tag $cy_kit_tag)
cy_kit_image=$base_py-cy_kit:$cy_kit_tag_build
buildFunc $base_py-cy_kit $cy_kit_tag_build $repositiory/$user/$cython_image $os
#------------ cy_web -------------------
rm -f $base_py-cy_web && cp -f ./templates/cy_web ./$base_py-cy_web
cy_web_tag=1
cy_web_tag_build=$(tag $cy_web_tag)
cy_web_image=$base_py-cy_web:$cy_web_tag_build
buildFunc $base_py-cy_web $cy_web_tag_build $repositiory/$user/$cython_image $os
#------------ cy_docs -------------------
rm -f $base_py-cy_docs && cp -f ./templates/cy_docs ./$base_py-cy_docs
cy_docs_tag=1
cy_docs_tag_build=$(tag $cy_docs_tag)
cy_docs_image=$base_py-cy_docs:$cy_docs_tag_build
buildFunc $base_py-cy_docs $cy_docs_tag_build $repositiory/$user/$cython_image $os
#------------ cy_env -------------------
#rm -f $base_py-cy-env && cp -f ./templates/cy-env ./$base_py-cy-env
#cy_env_tag=2
#cy_env_image=$base_py-cy-env:$cy_env_tag
#buildFunc $base_py-cy-env $cy_env_tag $top_image $os
#------------ cy_env -------------------
rm -f $base_py-cy-env && cp -f ./templates/cy-env ./$base_py-cy-env-cpu
cy_env_cpu_tag=1
cy_env_cpu_tag_build=$(tag $cy_env_cpu_tag)
cy_env_image=$base_py-cy-env-cpu:$cy_env_cpu_tag_build
buildFunc $base_py-cy-env-cpu $cy_env_cpu_tag_build $repositiory/$user/$torch_image
#---------------- cy-core-------------------
rm -f $base_py-cy-core
echo "
FROM $repositiory/$user/$fast_client_image as fast_client
FROM $repositiory/$user/$cy_es_image as es
FROM $repositiory/$user/$cy_kit_image as kit
FROM $repositiory/$user/$cy_docs_image as docs
FROM $repositiory/$user/$cy_web_image as web
FROM $repositiory/$user/$cy_env_image as env
FROM $top_image
COPY --from=fast_client /app /app
COPY --from=es /app /app
COPY --from=kit /app /app
COPY --from=docs /app /app
COPY --from=web /app /app
COPY --from=env /usr /usr

">>$base_py-cy-core
cy_core_tag=$(($fast_client_tag+$cy_es_tag+$cy_kit_tag+$cy_docs_tag+$cy_web_tag$cy_env_tag2))
cy_core_tag_build=$(tag $cy_core_tag)
cy_core_image=$base_py-cy-core:$cy_core_tag_build
buildFunc $base_py-cy-core $cy_core_tag_build $top_image $os
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
#export BUILDKIT_PROGRESS=
#export platform=linux/amd64,linux/arm64/v8
#export platform_=linux/amd64

com_tag=$(($libreoffice_tag+$dotnet_tag+$tessract_tag+$javac_tag+$opencv_tag))
com_tag_build=$(tag $com_tag)
com_image=$base_py-com:$com_tag_build
buildFunc $base_py-com $com_tag_build $top_image $os
#----- app-framework--------------
rm -f $base_py-xdoc-framework
echo "

FROM $repositiory/$user/$deep_learning_image as dlrn
FROM $repositiory/$user/$cy_core_image as core
FROM $repositiory/$user/$cy_env_image  as env
FROM $repositiory/$user/$com_image
#COPY --from=com / /
COPY --from=dlrn /usr /usr
COPY --from=core /usr /usr
COPY --from=core /app /app
COPY --from=env /usr /usr/
RUN pip uninstall pymongo -y && rm -fr /check
RUN apt install python3-opencv
">>$base_py-xdoc-framework
xdoc_framework_tag=cpu.$com_tag.$deep_learning_tag.$cy_env_cpu_tag
xdoc_framework_tag_build=$(tag $xdoc_framework_tag)
xdoc_framework_image=$base_py-xdoc-framework:$xdoc_framework_tag_build
buildFunc $base_py-xdoc-framework $xdoc_framework_tag_build $top_image $os
#----- apps--------------
rm -f $base_py-xdoc && cp -f ./templates/xdoc ./$base_py-xdoc
xdoc_tag=$xdoc_framework_tag.1
xdoc_tag_build=$(tag $xdoc_tag)
xdoc_image=$base_py-xdoc:$xdoc_tag_build
buildFunc $base_py-xdoc $xdoc_tag_build $repositiory/$user/$xdoc_framework_image $os
#--------------------------------------------------

echo "----------------------------------------------"
echo " In order to run image with arm64 platform:"
echo "1-install:
      sudo apt-get install qemu binfmt-support qemu-user-static
      2- docker run --platform=linux/arm64/v8  ...
      example:
      docker run --platform=linux/arm64/v8 \
        -v /home/vmadmin/python/v6/file-service-02/from-image-build/arm64:/app \
        $repositiory/$user/$cy_core_image python3 -c 'import time;time.sleep(100000000)'"
echo "---------------------------------------------------"
echo "------------deep learning framework----------------"
echo "docker run $repositiory/$user/$detectron2_image"
echo "docker run $repositiory/$user/$huggingface_image"
echo "docker run $repositiory/$user/$deepdoctection_image"
echo "docker run $repositiory/$user/$deep_learning_image python3 -c 'import time;time.sleep(100000000)'"
echo "------------------------------------------"
echo "docker run $repositiory/$user/$fast_client_image python3 -c 'import time;time.sleep(100000000)'"
echo "docker run $repositiory/$user/$cy_es_image python3 -c 'import time;time.sleep(100000000)'"
echo "docker run $repositiory/$user/$cy_kit_image python3 -c 'import time;time.sleep(100000000)'"
echo "docker run $repositiory/$user/$cy_docs_image python3 -c 'import time;time.sleep(100000000)'"
echo "docker run $repositiory/$user/$cy_web_image python3 -c 'import time;time.sleep(100000000)'"
echo "docker run $repositiory/$user/$cy_core_image python3 -c 'import time;time.sleep(100000000)'"

echo "------------------------------------------"
echo "test:"
echo "docker run $repositiory/$user/$com_image /check/libreoffice.sh"
echo "docker run $repositiory/$user/$com_image /check/tessract.sh"
echo "docker run $repositiory/$user/$com_image python3 /check/tika_server.py"
echo "docker run $repositiory/$user/$com_image python3 /check/dotnet.py"
echo "docker run $repositiory/$user/$com_image python3 /check/py_vncorenlp_check.py"
echo "docker run $repositiory/$user/$com_image python3 /check/opencv_check.py"
echo "docker run $repositiory/$user/$com_image python3 -c 'import time;time.sleep(100000000)'"
echo "docker run -p 8012:8012 $repositiory/$user/$xdoc_image python3  /app/cy_xdoc/server.py"
echo "docker run -p 8012:8012 $repositiory/$user/$xdoc_image /app/start.sh"
echo "Create volume:

docker volume create --name xdoc-data


"

#docker run docker docker.lacviet.vn/xdoc/py311-deepdoctection:1 python3 -c 'import time;time.sleep(100000000)'
#py3_dotnet=1
#buildFunc $base_py-dotnet $py3_dotnet
#docker buildx create --use --config /etc/containerd/config.toml