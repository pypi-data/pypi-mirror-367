from kres.subparsers.initParser    import InitParser
from kres.subparsers.logoutParser  import LogOutParser
from kres.subparsers.apiParser     import APIParser
from kres.subparsers.accessParser  import AccessParser
from kres.subparsers.restartParser import RestartParser
from kres.utils.parser             import Parser

class KresCLI:
    def __init__(self):
        self.parser = Parser()
        self.args   = self.parser.parse()

    def run(self):
        if self.args.command == 'init':
            InitParser(self.args).execute()

        elif self.args.command == 'logout':
            LogOutParser(self.args).execute()

        elif self.args.command == 'api':
            APIParser(self.args).execute()

        elif self.args.command == 'access':
            AccessParser(self.args).execute()
            
        elif self.args.command == 'restart':
            if self.parser.validateRestartParser(self.args):
                RestartParser(self.args).execute()

def main():
    KresCLI().run()