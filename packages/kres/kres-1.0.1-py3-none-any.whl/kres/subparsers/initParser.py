import json
from pathlib import Path
from getpass import getpass

from kres.config.extractConfig  import ExtractConfig
from kres.utils.checkPortStatus import CheckPortStatus
from kres.api.kresApiLauncher   import KresApiLauncher
from kres.utils.logger          import Logger

class InitParser:
    def __init__(self, args):
        self.args    = args
        self.kresDir = Path.home() / ".kres" / "init"
        self.kresDir.mkdir(parents=True, exist_ok=True)
        self.port    = None

        self.kresApiLauncher = KresApiLauncher(args.log)
        self.logger          = Logger(args.log)

        self.logger.debug(f"InitParser initialized with args: {self.args}")
        self.logger.debug(f"Configuration directory set to: {self.kresDir}")


    def execute(self) -> None:
        self.logger.info("Starting Kres initialization...")

        paraphrase = getpass("Provide the paraphrase to encrypt the kubeconfig SA token: ")
        self.logger.debug("Paraphrase collected successfully.")

        checkPortStatus = CheckPortStatus(self.args.port, self.args.log) if self.args.port else CheckPortStatus(self.args.log)
        
        if checkPortStatus.isPortOpen():
            self.logger.error(f"Port {checkPortStatus.port} is already in use. Please specify a different port or kill the process using that port.")
            return
        
        self.port = checkPortStatus.port

        extractConfig = ExtractConfig(self.args.kubeconfig, self.args.log) if self.args.kubeconfig else ExtractConfig(self.args.log)

        inputs = extractConfig.extractConfig()
        token  = extractConfig.extractToken()

        process = self.kresApiLauncher.launchKresApi(
            port       = self.port,
            token      = token,
            paraphrase = paraphrase
        )

        self.storeConfig(inputs)        
        self.storeKresApi({"pid": process.pid, "port": self.port})

        self.logger.info("Kres initialization complete.")


    def storeConfig(self, inputs: dict) -> None:
        self.logger.debug("Storing extracted config...")

        try:
            with open(self.kresDir / "kc.json", "w") as f:
                json.dump(inputs, f, indent=4)
            self.logger.debug("kc.json written successfully.")
        except Exception as e:
            self.logger.error(f"Failed to write kc.json: {e}")


    def storeKresApi(self, pid: str) -> None:
        self.logger.debug("Storing Kres API process details...")

        try:
            with open(self.kresDir / "kresApi.json", "w") as f:
                json.dump(pid, f, indent=4)
            self.logger.debug("kresApi.json written successfully.")
        except Exception as e:
            self.logger.error(f"Failed to write kresApi.json: {e}")