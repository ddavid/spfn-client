import sys, signal


class ServerSignalHandler(object):
    def __init__(self, Server):
        self.Server = Server
        signal.signal(signal.SIGINT, self.handle_signal)

    def handle_signal(self, sig, frame):
        print('You pressed Ctrl+C!')
        self.Server.cleanup()