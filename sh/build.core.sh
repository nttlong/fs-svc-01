#!/bin/sh
cd /home/vmadmin/python/v6/file-service-02
python compact.py /home/vmadmin/python/v6/file-service-02/bson dev
python compact.py /home/vmadmin/python/v6/file-service-02/pymongo dev
python compact.py /home/vmadmin/python/v6/file-service-02/gridfs dev
python compact.py /home/vmadmin/python/v6/file-service-02/elasticsearch dev
