#!/bin/sh
#apt update && apt upgrade && apt install wget -y && apt-get -y install make
#wget https://github.com/Kitware/CMake/releases/download/v3.24.2/cmake-3.24.2.tar.gz  && tar -zxvf cmake-3.24.2.tar.gz
#cd cmake-3.24.2  && ./bootstrap make
#cd ..

#apt-get install libreadline-gplv2-dev -y
#apt-get install libncursesw5-dev -y
#apt-get install libssl-dev -y
#apt-get install libsqlite3-dev -y
#apt-get install tk-dev -y
#apt-get install libgdbm-dev -y
##     libssl-dev
#apt-get install libssl-dev -y
#apt-get install  libsqlite3-dev -y
#apt-get install tk-dev -y
#apt-get install libgdbm-dev -y
#apt-get install libc6-dev -y
#apt-get install libbz2-dev -y
#apt-get install libffi-dev -y
#apt-get install zlib1g-dev -y
#
#apt install wget build-essential libreadline-gplv2-dev libncursesw5-dev \
#     libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev
wget https://www.python.org/ftp/python/3.9.5/Python-3.9.16.tgz && tar xzf Python-3.9.16.tgz && cd Python-3.9.16
./configure --enable-optimizations
make altinstall