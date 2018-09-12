import ocdskingfisher.status
import ocdskingfisher.cli.commands.base
import ocdskingfisher.sources_util


class StatusCLICommand(ocdskingfisher.cli.commands.base.CLICommand):
    command = 'status'

    def configure_subparser(self, subparser):
        subparser.add_argument("source", help="Which source do you want to see status for?")
        subparser.add_argument("--dataversion", help="Specify a data version - defaults to latest one")
        subparser.add_argument("--sample", help="See status for a sample", action="store_true")

    def run_command(self, args):

        source_id = args.source

        sources = ocdskingfisher.sources_util.gather_sources()

        if source_id not in sources:
            print("You must specify a source!")
            print("You can specify:")
            for source_id, source_info in sorted(sources.items()):
                print(" - %s" % source_id)
            quit(-1)

        source_status = ocdskingfisher.status.SourceStatus(base_dir=self.config.data_dir,
                                                           source_id=source_id,
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
