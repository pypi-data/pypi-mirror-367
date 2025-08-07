import socket

from kres.utils.logger import Logger

class CheckPortStatus:
    def __init__(self, port, log:str ="INFO") -> None:
        self.port   = int(port)
        self.logger = Logger(level=log)

    def isPortOpen(self) -> bool:
        self.logger.debug(f"Checking if port {self.port} is open on localhost...")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(("127.0.0.1", self.port))
            if result == 0:
                self.logger.debug(f"Port {self.port} is open.")
                return True
            else:
                self.logger.debug(f"Port {self.port} is not open.")
                return False