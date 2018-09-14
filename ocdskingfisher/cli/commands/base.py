import ocdskingfisher.sources_util
import ocdskingfisher.database


class CLICommand:
    command = ''

    def __init__(self, config=None):
        self.collection_instance = None
        self.config = config

    def configure_subparser(self, subparser):
        pass

    def run_command(self, args):
        pass

    def configure_subparser_for_selecting_existing_collection(self, subparser):
        subparser.add_argument("source", help="source")
        subparser.add_argument("--dataversion", help="Specify a data version")
        subparser.add_argument("--sample", help="Sample source only", action="store_true")

    def run_command_for_selecting_existing_collection(self, args):

        sources = ocdskingfisher.sources_util.gather_sources()

        sample_mode = args.sample
        data_version = args.dataversion

        if args.source not in sources:
            print("We can not find the source that you requested!")
            quit(-1)

        # This will raise an error if the version specified does not exist on disk.
        self.collection_instance = sources[args.source](self.config.data_dir,
                                                        remove_dir=False,
                                                        sample=sample_mode,
                                                        data_version=data_version,
                                                        new_version=False
                                                        )
