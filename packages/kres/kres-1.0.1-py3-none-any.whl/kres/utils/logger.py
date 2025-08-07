import sys
from datetime import datetime

class Logger:
    LEVELS = {
        "DEBUG"   : 10,
        "INFO"    : 20,
        "WARNING" : 30,
        "ERROR"   : 40
    }

    COLORS = {
        "DEBUG"   : "\033[94m",    # Blue
        "INFO"    : "\033[92m",     # Green
        "WARNING" : "\033[93m",  # Yellow
        "ERROR"   : "\033[91m",    # Red
        "RESET"   : "\033[0m"
    }

    def __init__(self, level:str = "INFO") -> None:
        self.level = self.LEVELS.get(level.upper(), 20)

    def log(self, message:str , level_name:str) -> None:
        if self.LEVELS[level_name] >= self.level:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            color     = self.COLORS.get(level_name, "")
            reset     = self.COLORS["RESET"]
            output_stream = sys.stderr if level_name == "ERROR" else sys.stdout
            print(f"{color}[{timestamp}] [{level_name}] {message}{reset}", file=output_stream)

    def debug(self, message:str) -> None:
        self.log(message, "DEBUG")

    def info(self, message:str) -> None:
        self.log(message, "INFO")

    def warning(self, message:str) -> None:
        self.log(message, "WARNING")

    def error(self, message:str) -> None:
        self.log(message, "ERROR")
