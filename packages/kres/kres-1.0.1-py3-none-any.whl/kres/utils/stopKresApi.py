import os
import json
import signal
from pathlib import Path

from kres.utils.logger import Logger

class StopKresApi:
    def __init__(self, log:str = "INFO") -> None:
        self.logger      = Logger(log)
        self.kresDdir    = Path.home() / ".kres" / "init"
        self.kresApiFile = self.kresDdir / "kresApi.json"

        self.logger.debug(f"Looking for Kres API metadata at {self.kresApiFile}")

        try:
            with open(self.kresApiFile, "r") as f:
                self.kresApiData = json.load(f)
                self.logger.debug("Successfully loaded kresApi.json")
        except FileNotFoundError as e:
            self.logger.error(f"Kres API configuration file not found. Please run 'kres init' to set up the Kres API server. {e}")
            return

    def stop(self) -> None:
        pid = self.kresApiData.get('pid')
        try:
            self.logger.debug(f"Attempting to stop process with PID: {pid}")
            os.kill(pid, signal.SIGTERM)
            self.logger.info(f"Kres API process (PID {pid}) terminated successfully.")
        except ProcessLookupError as p:
            self.logger.warning(f"Kres API process (PID {pid}) was not running. {p}")
        except Exception as e:
            self.logger.error(f"Failed to terminate Kres API process (PID {pid}): {e}")
            return