#!/bin/sh

apt update && apt-get install wget -y
apt install mono-complete -y
python3 -m  pip install --upgrade pip
python3 -m pip uninstall pythonnet -y
python3 -m pip install pythonnet==3.0.1
python3 /check/dotnet.py
