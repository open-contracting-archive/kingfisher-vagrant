import os
import ocdsdata.status
import ocdsdata.cli.commands.base
import ocdsdata.sources_util


class StatusCLICommand(ocdsdata.cli.commands.base.CLICommand):
    command = 'status'

    def configure_subparser(self, subparser):
        subparser.add_argument("source", help="Which source do you want to see status for?")
        subparser.add_argument("--dataversion", help="Specify a data version - defaults to latest one")
        subparser.add_argument("--sample", help="See status for a sample", action="store_true")
        subparser.add_argument("--basedir", help="base dir - defaults to 'data' on current directory")
        subparser.add_argument("--outputdir", help="output dir - defaults to source id.")

    def run_command(self, args):

        this_dir = os.path.dirname(os.path.realpath(__file__))
        base_dir = args.basedir or os.path.join(this_dir, "..", "..", "..", "data")

        source_id = args.source

        sources = ocdsdata.sources_util.gather_sources()

        if source_id not in sources:
            print("You must specify a source!")
            print("You can specify:")
            for source_id, source_info in sorted(sources.items()):
                print(" - %s" % source_id)
            quit(-1)

        source_status = ocdsdata.status.SourceStatus(base_dir=base_dir,
                                                     source_id=source_id,
                                                     output_directory=args.outputdir,
                                                     sample=args.sample,
                                                     data_version=args.dataversion
                                                     )

        print("Status for: %s (Output Dir: %s, Data Version: %s)" % (
            source_id, source_status.output_directory, source_status.data_version))

        if not source_status.is_gather_finished():
            print("####### Gather Progress")
            print(source_status.get_gather_progress_as_text())
        elif not source_status.is_fetch_finished():
            print("####### Fetch Progress")
            print(source_status.get_fetch_progress_as_text())
        elif not source_status.is_store_finished():
            print("####### Store Progress")
            print(source_status.get_store_progress_as_text())
        elif not source_status.is_check_finished():
            print("####### Check Progress")
            print(source_status.get_check_progress_as_text())
        else:
            print("Gather, Fetch, Store and Check all Finished!")
