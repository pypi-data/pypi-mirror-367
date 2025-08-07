import argparse

class Parser:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            prog        = 'kres',
            description = "Kubernetes Restarter 'kres' CLI tool"
        )

        self.subParser = self.parser.add_subparsers(
            dest     = 'command',
            required = True
        )

        self.initParser()
        self.logoutParser()
        self.apiParser()
        self.accessParser()
        self.restartParser()

    def initParser(self) -> None:
        initParser = self.subParser.add_parser(
            "init", help = "Initialize with the given kubeconfig"
        )

        initParser.add_argument(
            "-k", "--kubeconfig",
            help = "Path to the kubeconfig file. Default value '~/.kube/config'"
        )

        initParser.add_argument(
            "-p", "--port",
            help    = "Port on which kres API will run. Default port is 5454",
            type    = int,
            default = 5454
        )

        initParser.add_argument(
            "--log",
            help    = "Log level for kres CLI. Default is 'INFO'",
            choices = ["DEBUG", "INFO", "WARNING", "ERROR"],
            default = "INFO"
        )

    def logoutParser(self) -> None:
        logoutParser = self.subParser.add_parser(
            "logout", help = "Logs out from kres. Deletes kubeconfig and paraphrase from the session"
        )

        logoutParser.add_argument(
            "--log",
            help    = "Log level for kres CLI. Default is 'INFO'",
            choices = ["DEBUG", "INFO", "WARNING", "ERROR"],
            default = "INFO"
        )

    def apiParser(self) -> None:
        apiParser = self.subParser.add_parser(
            "api", help = "Check Kuberneted API metrics"
        )

        apiParser.add_argument(
            "-t", "--type",
            help = "Type of API to check. Kres API or Kubernetes API [kres, kubernetes]",
        )

        apiParser.add_argument(
            "--log",
            help    = "Log level for kres CLI. Default is 'INFO'",
            choices = ["DEBUG", "INFO", "WARNING", "ERROR"],
            default = "INFO"
        )

    def accessParser(self) -> None:
        accessParser = self.subParser.add_parser(
            "access", help = "Check if Kres can access the resources in the namespace"
        )

        accessParser.add_argument(
            "-n", "--namespace",
            help     = "Namespace of the resource to access",
            required = True
        )

        accessParser.add_argument(
            "-r", "--resource",
            help     = "Resource to access",
            choices  = ["pods", "deployments", "statefulsets", "services", "configmaps", "secrets"],
            required = True
        )

        accessParser.add_argument(
            "-v", "--verb",
            help     = "Verb to check access for the resource",
            choices  = ["get", "list", "watch", "create", "update", "patch", "delete"],
            required = True
        )

        accessParser.add_argument(
            "--log",
            help    = "Log level for kres CLI. Default is 'INFO'",
            choices = ["DEBUG", "INFO", "WARNING", "ERROR"],
            default = "INFO"
        )

    def restartParser(self) -> None:
        restartParser = self.subParser.add_parser(
            "restart", help = "Restart the specified resource in the namespace"
        )

        restartParser.add_argument(
            "-n", "--namespace",
            help     = "Namespace of the resource to restart",
            required = True
        )

        restartParser.add_argument(
            "-r", "--resource",
            help     = "Resource type to restart",
            choices  = ["deployments", "statefulsets", "pods"],
            required = True
        )

        group = restartParser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--all", 
            help   = "Restart all resources of the specified type in the namespace",
            action = 'store_true'
        )
        group.add_argument(
            "-i", "--name",
            help    = "Name of the resource to restart",
            default = None,
        )

        restartParser.add_argument(
            "-s", "--secret",
            help     = "Name of the Secret to check for in the resources",
            default  = "",
            required = False
        )

        restartParser.add_argument(
            "-c", "--configmap",
            help     = "Name of the ConfigMap to check for in the resources",
            default  = "",
            required = False
        )

        restartParser.add_argument(
            "--reason",
            help    = "Reason for the restart",
            default = "Restarted by kres CLI"
        )

        restartParser.add_argument(
            "--log",
            help    = "Log level for kres CLI. Default is 'INFO'",
            choices = ["DEBUG", "INFO", "WARNING", "ERROR"],
            default = "INFO"
        )

    def parse(self) -> None:
        return self.parser.parse_args()

    def validateRestartParser(self, args) -> None:
        if args.all and not (args.secret or args.configmap):
            self.parser.error("When using --all, at least one of --secret or --configmap must be specified.")
            return False
        
        return True