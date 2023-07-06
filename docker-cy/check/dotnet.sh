#!/bin/sh
python3 -m pip uninstall pythonnet -y
python3 -m pip install pythonnet==3.0.1
python3 /check/dotnet.py
killall dotnet; exit 0