#!/bin/bash

docker login https://docker.lacviet.vn -u xdoc -p Lacviet#123
export user=xdoc
export platform=linux/amd64
export platform_=linux/amd64,linux/arm64/v8
export generation=adm.1
export generation_=1
export repositiory=docker.lacviet.vn
export push=docker.lacviet.vn/xdoc

chmod +x debian-p.sh
chmod +x debian-pod.sh
chmod +x debian-podc.sh
chmod +x debian-podc-framework.sh

#./debian-p.sh 1
./debian-pod.sh 1
#./debian-podc.sh 1
#./debian-podc-framework.sh 1

