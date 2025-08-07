import json
from pathlib import Path

from kres.utils.logger import Logger

class ReadMemory:
    def __init__(self, log:str = "INFO") -> None:
        self.logger      = Logger(log)
        self.kresDir     = Path.home() / ".kres" / "init"
        self.kresApiFile = self.kresDir / "kresApi.json"

    def readJson(self) -> dict:
        self.logger.debug(f"Attempting to read Kres config from: {self.kresDir / 'kc.json'}")

        try:
            with open(self.kresDir / "kc.json", "r") as f:
                data = json.load(f)
                self.logger.debug("Successfully loaded kc.json.")
        except FileNotFoundError:
            self.logger.error("Kres configuration file not found. Please run 'kres init' to set up the Kres API server.")
            return

        return data
    
    def readKresApiData(self) -> dict:
        self.logger.debug(f"Attempting to read Kres API data from: {self.kresApiFile}")

        try:
            with open(self.kresApiFile, "r") as f:
                kresApiData = json.load(f)
                self.logger.debug("Successfully loaded kresApi.json.")
        except FileNotFoundError:
            self.logger.error("Kres API configuration file not found. Please run 'kres init' to set up the Kres API server.")
            return
        
        return kresApiData