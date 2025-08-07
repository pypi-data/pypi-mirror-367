from kres.config.loadConfig import LoadConfig
from kres.utils.logger      import Logger

class ExtractConfig:
    def __init__(self, kubeConfigPath: str = "~/.kube/config", log: str = "INFO") -> None:
        self.logger         = Logger(log)
        self.kubeConfigPath = kubeConfigPath
        self.config         = LoadConfig(self.kubeConfigPath, log).loadConfig()

    def extractConfig(self) -> dict[str, str]:
        apiServer = None
        caAuth    = None

        self.logger.debug("Extracting cluster information from kubeconfig...")
        for cluster in self.config['clusters']:
            try:
                apiServer = cluster['cluster']['server']
            except Exception:
                self.logger.error("Missing 'server' key in kubeconfig")
                raise ValueError("Missing 'server' key in kubeconfig")

            try:
                caAuth = cluster['cluster']['certificate-authority']
            except Exception:
                self.logger.error("Missing 'certificate-authority' key in kubeconfig")
                raise ValueError("Missing 'certificate-authority' key in kubeconfig")

            self.logger.debug(f"Found API server: {apiServer}")
            self.logger.debug(f"Found CA path: {caAuth}")

        self.logger.debug("Cluster information extracted successfully.")
        return {'apiServer': apiServer, 'caAuth': caAuth}

    def extractToken(self) -> str | None:
        self.logger.debug("Extracting user token from kubeconfig...")

        bearerToken = None

        for user in self.config['users']:
            try:
                bearerToken = user['user']['token']
            except Exception:
                self.logger.error("Missing 'token' key in kubeconfig")
                raise ValueError("Missing 'token' key in kubeconfig")

        self.logger.debug("Bearer token extracted successfully.")
        return bearerToken