import os
import yaml

from kres.utils.logger import Logger

class LoadConfig:
    def __init__(self, kubeConfigPath: str = "~/.kube/config", log: str = "INFO") -> None:
        self.logger        = Logger(log)
        self.kubeConfigPath = os.path.expanduser(kubeConfigPath)

        self.logger.debug(f"Expanded kubeConfig path: {self.kubeConfigPath}")

    def loadConfig(self) -> dict:
        self.logger.debug("Loading kubeconfig...")

        if not os.path.exists(self.kubeConfigPath):
            self.logger.error(f"Kubeconfig not found at: {self.kubeConfigPath}")
            raise FileNotFoundError(f"Kubeconfig not found at: {self.kubeConfigPath}")

        with open(self.kubeConfigPath, 'r') as file:
            config = yaml.safe_load(file)
            self.logger.debug("Kubeconfig loaded and parsed successfully.")

        requiredKeys = ['apiVersion', 'clusters', 'users', 'contexts']

        for key in requiredKeys:
            if key not in config:
                self.logger.error(f"Missing required key '{key}' in kubeconfig")
                raise ValueError(f"Missing '{key}' in kubeconfig")

        self.logger.debug("Kubeconfig loaded and validated successfully.")
        return config