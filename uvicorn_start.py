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
import os
import sys
for x in sys.argv:
    print(x)
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve

import enig_frames.containers
log=enig_frames.containers.Container.loggers.get_logger("web")
log.info(f"Start web from {__file__}")
import uvicorn
from api_app import app
print("shoul call with w:4")
worker = 4
for x in sys.argv:
        if x.startswith('w:'):
                worker =int(x.split(':')[1])
print(f"worker={worker}")
if __name__ == "__main__":
        import signal

        signal.signal(signal.SIGCHLD, signal.SIG_IGN)


        timeout_keep_alive = enig_frames.containers.Container.config.config.timeout_keep_alive
        interface = 'auto'
        if enig_frames.containers.Container.config.config.interface:
                interface = enig_frames.containers.Container.config.config.interface
        print(f"Inteface {interface}")
        if timeout_keep_alive is None:
                timeout_keep_alive=5
        uvicorn.run(
                "api_app:app",
                host= enig_frames.containers.Container.config.config.binding_ip,
                port=int(enig_frames.containers.Container.config.config.binding_port),
                workers=worker,
                ws='websockets',
                ws_max_size=16777216*1024,
                backlog=1000,
                interface=interface,

                # timeout_keep_alive=timeout_keep_alive,
                lifespan='on'
                # reload=False,

            )
