#!/bin/sh
python3 -m pip uninstall py-vncorenlp -y
python3 -m pip install py-vncorenlp==0.1.4
python3 /check/py_vncorenlp_check.py
