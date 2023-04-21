import sys
import time


class App(object):
    def __init__(self,on_start, on_stop_handler):
        self.on_stop_handler = on_stop_handler
        self.on_start = on_start
        if sys.platform == "linux":
            import signal
            signal.signal(signal.SIGCHLD, signal.SIG_IGN)
            self.shutdown = False
            # Registering the signals
            signal.signal(signal.SIGINT, self.exit_graceful)
            signal.signal(signal.SIGTERM, self.exit_graceful)
            signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        else:
            print(f"It does not support for {sys.platform}")
    def start(self):
        pass
    def exit_graceful(self, signum, frame):
        print('Received:', signum, ": ", frame)
        self.shutdown = True

    def run(self):
        time.sleep(1)
        print("running App: ")

    def stop(self):
        # clean up the resources
        self.on_stop_handler()
        print("stop the app")




if __name__ == "__main__":
    app = App()
    app.start()

    while not app.shutdown:
        app.run()

    app.stop()
    sys.exit(0)