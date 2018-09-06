import ocdskingfisher.database
import ocdskingfisher.cli.commands.base


class UpgradeDataBaseCLICommand(ocdskingfisher.cli.commands.base.CLICommand):
    command = 'upgrade-database'

    def configure_subparser(self, subparser):
        subparser.add_argument("--deletefirst", help="Delete Database First", action="store_true")

    def run_command(self, args):

        if args.deletefirst:
            if args.verbose:
                print("Dropping Database")
            ocdskingfisher.database.delete_tables()

        if args.verbose:
            print("Upgrading/Creating Database")
        ocdskingfisher.database.create_tables()
