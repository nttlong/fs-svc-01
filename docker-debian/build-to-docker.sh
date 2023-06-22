#!/bin/bash
export user=nttlong/xdoc
export platform=linux/amd64
export generation=adm.1
export muli_platform=linux/amd64,linux/arm64/v8
export repositiory=hub.docker.com
export push=nttlong
chmod +x debian-py-39.sh
chmod +x debian-dot-net-core-6-7.sh
chmod +x debian-component.sh
chmod +x debian-libre-office.sh
./debian-py-39.sh
#./debian-dot-net-core-6-7.sh
#./debian-component.sh
#./debian-libre-office.sh