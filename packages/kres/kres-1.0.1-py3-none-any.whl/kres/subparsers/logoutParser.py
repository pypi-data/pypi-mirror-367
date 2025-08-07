from kres.utils.logger      import Logger
from kres.utils.stopKresApi import StopKresApi
from kres.utils.deleteDir   import DeleteDir

class LogOutParser:
    def __init__(self, args) -> None:
        self.args   = args
        self.logger = Logger(args.log)

        self.logger.debug(f"LogoutParser initialized with args: {self.args}")

        self.stopKresApi = StopKresApi(log=args.log)
        self.deleteDir   = DeleteDir("init", log=args.log)

    def execute(self) -> None:
        self.logger.info("Logging out from kres...")
        
        self.stopKresApi.stop()
        self.deleteDir.delete()