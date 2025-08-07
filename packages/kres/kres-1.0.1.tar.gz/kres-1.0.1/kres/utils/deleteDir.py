import shutil
from pathlib import Path

from kres.utils.logger import Logger

class DeleteDir:
    def __init__(self, file_path: str, log:str ="INFO") -> None:
        self.kresDir  = Path.home() / ".kres"
        self.dir_path = self.kresDir / file_path
        self.logger   = Logger(log)

    def delete(self) -> None:
        try:
            self.logger.debug(f"Deleting directory: {self.dir_path}")
            shutil.rmtree(self.dir_path)
            self.logger.info(f"Directory {self.dir_path} deleted successfully.")
        except Exception as e:
            self.logger.error(f"Failed to delete directory {self.dir_path}: {e}")
            raise e