import subprocess
import ocdsdata.database
import ocdsdata.cli.commands.base
import ocdsdata.maindatabase.config


class DBShellCommand(ocdsdata.cli.commands.base.CLICommand):
    command = 'dbshell'

    def __init__(self):
        self.uri = ocdsdata.maindatabase.config.DB_URI

    def run_command(self, args):
        print("Starting a PSQL Shell.")
        shell = subprocess.run(["psql", self.uri])
