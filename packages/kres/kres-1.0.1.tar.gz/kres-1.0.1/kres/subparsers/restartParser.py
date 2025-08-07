from kres.api.apiHandler import APIHandler
from kres.utils.logger   import Logger

class RestartParser:
    def __init__(self, args) -> None:
        self.args       = args
        self.apiHandler = APIHandler(log=args.log)
        self.logger     = Logger(level=args.log)

        self.logger.debug(f"RestartParser initialized with args: {self.args}")

    def execute(self) -> None:
        self.logger.info("Checking Kubernetes API server status...")
        
        if not self.apiHandler.isKubeApiRunning():
            self.logger.error("Kubernetes API server is not reachable.")
            return
        
        self.logger.info(f"Preparing to restart resource: {self.args.resource} in namespace: {self.args.namespace}")

        if self.args.resource == "pods":
            self.logger.warning("Warning: Deleting Pods directly is not the recommended way to reload ConfigMaps or Secrets.")
            self.logger.warning("Consider restarting the controller (Deployment/StatefulSet) instead to ensure proper resource reloading.")

            userConfirmation = input("Do you want to proceed with deleting the Pods? (y/N): ").strip().lower()

            if userConfirmation != 'y':
                self.logger.info("Operation cancelled by the user.")
                return
            else:
                self.logger.debug("User confirmed pod deletion.")
                verb = "delete"
        else:
            verb = "patch"

        self.logger.debug(f"Checking access for verb '{verb}' on {self.args.resource} in namespace {self.args.namespace}")

        access = self.apiHandler.checkResourceAccess(
            namespace = self.args.namespace,
            resource  = self.args.resource,
            verb      = verb
        )

        if not access:
            self.logger.error(f"No permission to {verb} {self.args.resource} in namespace {self.args.namespace}. Check RBAC policies or your role bindings.")
            return

        self.apiHandler.restartResource(
            namespace = self.args.namespace,
            resource  = self.args.resource,
            name      = self.args.name,
            secret    = self.args.secret,
            configmap = self.args.configmap,
            allFlag   = self.args.all,
            reason    = self.args.reason
        )