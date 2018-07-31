import os

import ocdsdata.database
import ocdsdata.cli.commands.base
import ocdsdata.sources_util


class CheckDifferentSchemaVersionCLICommand(ocdsdata.cli.commands.base.CLICommand):
    command = 'check-different-schema-version'

    def __init__(self):
        self.sources = ocdsdata.sources_util.gather_sources()

    def configure_subparser(self, subparser):
        subparser.add_argument("--run", help="source")
        subparser.add_argument("--dataversion", help="Specify a data version")
        subparser.add_argument("--basedir", help="base dir - defaults to 'data' on current directory")
        subparser.add_argument("--outputdir", help="output dir - defaults to id.")
        subparser.add_argument("--sample", help="Sample source only", action="store_true")
        subparser.add_argument("--schemaversion", help="Set Schema Version - defaults to 1.1")

    def run_command(self, args):

        this_dir = os.path.dirname(os.path.realpath(__file__))
        base_dir = args.basedir or os.path.join(this_dir, "..", "..", "..", "data")
        sample_mode = args.sample
        data_version = args.dataversion
        override_schema_version = args.schemaversion or "1.1"

        schema_versions = ["1.0", "1.1"]
        if override_schema_version not in schema_versions:
            print("We do not recognise that schema version! Options are: %s" % ", ".join(schema_versions))
            quit(-1)

        output_directory = args.outputdir or args.run

        if args.run not in self.sources:
            print("We can not find a source that you requested!")
            quit(-1)

        instance = self.sources[args.run](base_dir,
                                          remove_dir=False,
                                          output_directory=output_directory,
                                          sample=sample_mode,
                                          data_version=data_version,
                                          new_version=False
                                          )

        instance.run_check(override_schema_version)
