#!/bin/bash

docker login https://docker.lacviet.vn -u xdoc -p Lacviet#123
export user=xdoc
export platform=linux/amd64
export platform_=linux/amd64,linux/arm64/v8
export generation=adm.1
export generation_=1
export repositiory=docker.lacviet.vn
export push=docker.lacviet.vn/xdoc

#chmod +x debian-p.sh 1
chmod +x debian-pod.sh 1
chmod +x debian-podc.sh 1
chmod +x debian-podc-framework.sh 1

./debian-p.sh
./debian-pod.sh
./debian-podc.sh
./debian-podc-framework.sh

