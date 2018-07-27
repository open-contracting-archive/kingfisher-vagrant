import ocdsdata.cli.commands.base
import ocdsdata.sources_util


class CleanCLICommand(ocdsdata.cli.commands.base.CLICommand):
    command = 'clean'

    def __init__(self):
        self.sources = ocdsdata.sources_util.gather_sources()

    def configure_subparser(self, subparser):
        subparser.add_argument("source", help="Wipe this source data")

    def run_command(self, args):
        pass
