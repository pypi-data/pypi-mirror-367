from kres.api.apiHandler import APIHandler
from kres.utils.logger   import Logger

class APIParser:
    def __init__(self, args) -> None:
        self.args       = args
        self.logger     = Logger(level=args.log)
        self.apiHandler = APIHandler(log=args.log)

        self.logger.debug(f"APIParser initialized with args: {self.args}")
        
    def execute(self) -> None:
        self.logger.info(f"Checking status of {self.args.type} API...")

        if self.args.type == 'kres':
            if self.apiHandler.isKresApiRunning():
                self.logger.info("Kres API is running.")
            else:
                self.logger.error("Kres API is not running. Please start the Kres API server using kres init command.")

        elif self.args.type == 'kubernetes':
            if self.apiHandler.isKubeApiRunning():
                self.logger.info("Kubernetes API is reachable.")
            else:
                self.logger.error("Kubernetes API is not reachable. Please check your kubeconfig and network settings.")