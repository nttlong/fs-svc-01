#!/bin/sh
cd /home/vmadmin/python/v6/file-service-02
python compact.py /home/vmadmin/python/v6/file-service-02/cy_xdoc dev
python compact.py /home/vmadmin/python/v6/file-service-02/cy_web dev
python compact.py /home/vmadmin/python/v6/file-service-02/cy_utils dev
python compact.py /home/vmadmin/python/v6/file-service-02/cy_kit dev
python compact.py /home/vmadmin/python/v6/file-service-02/cy_es dev
python compact.py /home/vmadmin/python/v6/file-service-02/cy_docs dev