#!/bin/sh
pip uninstall pymonggo -y
pip uninstall elasticsearch -y
python3 /app/compact.py /app/pymongo
python3 /app/compact.py /app/bson
python3 /app/compact.py /app/elasticsearch
python3 /app/compact.py /app/gridfs
python3 /app/compact.py /app/cy_docs
python3 /app/compact.py /app/cy_utils
python3 /app/compact.py /app/cy_web
python3 /app/compact.py /app/cy_xdoc
python3 /app/compact.py /app/cyx
python3 /app/compact.py /app/cy_kit
python3 /app/compact.py /app/cy_es
