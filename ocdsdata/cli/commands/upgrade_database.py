import ocdsdata.database
import ocdsdata.cli.commands.base


class UpgradeDataBaseCLICommand(ocdsdata.cli.commands.base.CLICommand):
    command = 'upgrade-database'

    def configure_subparser(self, subparser):
        subparser.add_argument("--deletefirst", help="Delete Database First", action="store_true")

    def run_command(self, args):

        if args.deletefirst:
            if args.verbose:
                print("Dropping Database")
            ocdsdata.database.delete_tables()

        if args.verbose:
            print("Upgrading/Creating Database")
        ocdsdata.database.create_tables()
