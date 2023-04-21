"""
In order to start with hypercorn
   just use  python hypercorn_start.py
    You may also change default config.yml by past arguments
        For example in config.yml at (glance at config.yml at root top project)
            db:
               host: 192.168.18.26
               port: 27018
        if you would like to change db.port juts past db.port=<new port>
        Important: some item in config.yml could be removed at runtime id you set nothing
                    Example: some Mongod for developer needn't set authenticate
                        So you can pass db.usrername= db.password= db.authSource= db.authMechanism=
python hypercorn_start.py db.host=172.16.7.25 db.port=27018 db.username= db.password= db.authSource= db.authMechanism= admin_db_name=enigma-media
"""
import sys
for x in sys.argv:
    print(x)
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve

import enig_frames.containers
log=enig_frames.containers.Container.loggers.get_logger("web")
log.info(f"Start web from {__file__}")
from api_app import app
hyper_conf =Config()

hyper_conf.bind=[
    f"{enig_frames.containers.Container.config.config.binding_ip}:{enig_frames.containers.Container.config.config.binding_port}"
]
asyncio.run(serve(app, hyper_conf))