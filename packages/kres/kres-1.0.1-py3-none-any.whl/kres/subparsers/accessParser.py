from kres.api.apiHandler import APIHandler
from kres.utils.logger   import Logger

class AccessParser:
    def __init__(self, args) -> None:
        self.args       = args
        self.apiHandler = APIHandler(args.log)
        self.logger     = Logger(args.log)

        self.logger.debug(f"AccessParser initialized with args: {self.args}")

    def execute(self) -> None:
        self.logger.info("Starting access check for Kubernetes resource...")

        if self.apiHandler.isKubeApiRunning():
            self.logger.debug("Kubernetes API is reachable.")

            access = self.apiHandler.checkResourceAccess(
                namespace = self.args.namespace,
                resource  = self.args.resource,
                verb      = self.args.verb
            )

            if access:
                self.logger.info(
                    f"Access to {self.args.resource} in namespace {self.args.namespace} with verb '{self.args.verb}' is allowed."
                )
            else:
                self.logger.error(
                    f"Access to {self.args.resource} in namespace {self.args.namespace} with verb '{self.args.verb}' is denied."
                )
        else:
            self.logger.error("Kubernetes API is not reachable. Check kubeconfig or network settings.")