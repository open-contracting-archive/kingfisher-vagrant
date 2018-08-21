import logging
import ocdsdata.database
import ocdsdata.cli.commands.base


class UpgradeDataBaseCLICommand(ocdsdata.cli.commands.base.CLICommand):
    command = 'upgrade-database'

    def configure_subparser(self, subparser):
        subparser.add_argument("--deletefirst", help="Delete Database First", action="store_true")

    def run_command(self, args):

        if args.deletefirst:
            logging.debug("Dropping Database")
            ocdsdata.database.delete_tables()

        logging.debug("Upgrading/Creating Database")
        ocdsdata.database.create_tables()
