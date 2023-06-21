#!/bin/bash
apt-get install wget -y  build-essential -y
wget https://www.openssl.org/source/openssl-1.1.1q.tar.gz
tar -xzvf openssl-1.1.1q.tar.gz
cd openssl-1.1.1q
./config
make install