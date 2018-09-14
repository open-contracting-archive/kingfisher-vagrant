import ocdskingfisher.database
import ocdskingfisher.cli.commands.base


class ForceFetchToStoreCLICommand(ocdskingfisher.cli.commands.base.CLICommand):
    command = 'force-fetch-to-store'

    def configure_subparser(self, subparser):
        self.configure_subparser_for_selecting_existing_collection(subparser)

    def run_command(self, args):

        self.run_command_for_selecting_existing_collection(args)

        if not self.collection_instance.is_gather_finished():
            print("Gather is not finished; this must finish first!")
            quit(-1)

        if self.collection_instance.is_fetch_finished():
            print("Fetch is already finished; there is no need for this!")
            return

        self.collection_instance.force_fetch_to_gather()
        print("Forced!")
