import subprocess

from kres.utils.logger import Logger

class KresApiLauncher:
    def __init__(self, log: str = "INFO") -> None:
        self.logger = Logger(log)

    def launchKresApi(self, port: int, token: str, paraphrase: str) -> subprocess.Popen | None:
        self.logger.debug(f"Launching Kres API on port {port}...")

        try:
            process = subprocess.Popen(
                ["python3", "-m", "kres.api.kresApi", str(port)],
                stdin  = subprocess.PIPE,
                stdout = subprocess.DEVNULL,
                stderr = subprocess.DEVNULL,
            )
            self.logger.debug("Kres API subprocess started successfully.")
        except Exception as e:
            self.logger.error(f"Failed to start Kres API subprocess: {str(e)}")
            return None

        payload = f"{paraphrase}\n{token}\n"
        try:
            process.stdin.write(payload.encode())
            process.stdin.flush()
            self.logger.debug("Paraphrase and token passed to Kres API via stdin.")
        except Exception as e:
            self.logger.error(f"Failed to pass token/paraphrase to API: {str(e)}")

        self.logger.debug("Kres API launched and credentials passed successfully.")
        return process