import papermill as pm

pm.execute_notebook(
   '/home/vmadmin/python/v6/file-service-02/docker-build/cuelake/data/input.ipynb',
   '/home/vmadmin/python/v6/file-service-02/docker-build/cuelake/data/output.ipynb',
   parameters = dict(alpha=0.6, ratio=0.1)
)