#!/bin/bash

docker login https://docker.lacviet.vn -u xdoc -p Lacviet#123
export user=xdoc
export platform=linux/amd64
export platform_=linux/amd64,linux/arm64/v8
export generation=adm.1
export generation_=1
export repositiory=docker.lacviet.vn
export push=docker.lacviet.vn/xdoc

chmod +x debian-py-39.sh
chmod +x debian-dot-net-core-6-7.sh
chmod +x debian-component.sh
chmod +x debian-libre-office.sh
chmod +x debian-py-39-core.sh
chmod +x debian-py-39-core-framework.sh
chmod +x debian-py-39-app-framework.sh


#./debian-py-39.sh
#./debian-dot-net-core-6-7.sh
#./debian-component.sh
#./debian-libre-office.sh
#./debian-py-39-core.sh
#./debian-py-39-core-framework.sh
./debian-py-39-app-framework.sh

#xdoc/debian-libre-office
#xdoc/debian-component
#xdoc/debian-dot-net-core-6-7
#xdoc/debian-py-39
#xdoc/debian-py-framework-core