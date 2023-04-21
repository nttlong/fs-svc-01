import time

import cy_kit
logs = cy_kit.create_logs(
    log_dir="/home/vmadmin/python/v6/file-service-02/logs/test",
    name= "test_graceful_app"
)
def run():
    while True:
        time.sleep(1)
        print("running")
        logs.info("running")

def stop():
    print("Ok exit")
    logs.info("Ok exit")


if __name__ == "__main__":
    app = cy_kit.Graceful_Application(
        on_run=run,
        on_stop=stop
    )
    app.start()
