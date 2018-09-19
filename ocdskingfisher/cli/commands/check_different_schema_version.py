import ocdskingfisher.database
import ocdskingfisher.cli.commands.base


class CheckDifferentSchemaVersionCLICommand(ocdskingfisher.cli.commands.base.CLICommand):
    command = 'check-different-schema-version'

    def __init__(self, config=None):
        self.sources = ocdskingfisher.sources_util.gather_sources()
        self.config = config

    def configure_subparser(self, subparser):
        self.configure_subparser_for_selecting_existing_collection(subparser)
        subparser.add_argument("--schemaversion", help="Set Schema Version - defaults to 1.1")

    def run_command(self, args):

        self.run_command_for_selecting_existing_collection(args)

        override_schema_version = args.schemaversion or "1.1"

        schema_versions = ["1.0", "1.1"]
        if override_schema_version not in schema_versions:
            print("We do not recognise that schema version! Options are: %s" % ", ".join(schema_versions))
            quit(-1)

        self.collection_instance.run_check(override_schema_version)
