import os
import logging

import ocdsdata.cli.commands.base
import ocdsdata.sources_util
import ocdsdata.database


class RunCLICommand(ocdsdata.cli.commands.base.CLICommand):
    command = 'run'

    def __init__(self):
        self.sources = ocdsdata.sources_util.gather_sources()

    def configure_subparser(self, subparser):
        subparser.add_argument("source", help="run one or more sources", nargs="*")
        subparser.add_argument("--all", help="run all sources",	action="store_true")
        subparser.add_argument("--basedir", help="base dir - defaults to 'data' on current directory")

        subparser.add_argument("--onlygather", help="only run the gather stage", action="store_true")
        subparser.add_argument("--ignoregather", help="don't run the gather stage", action="store_true")
        subparser.add_argument("--onlyfetch", help="only run the fetch stage", action="store_true")
        subparser.add_argument("--ignorefetch", help="don't run the fetch stage", action="store_true")
        subparser.add_argument("--onlystore", help="only run the store stage", action="store_true")
        subparser.add_argument("--ignorestore", help="don't run the store stage", action="store_true")
        subparser.add_argument("--onlycheck", help="only run the check stage", action="store_true")
        subparser.add_argument("--ignorecheck", help="don't run the check stage", action="store_true")
        subparser.add_argument("--sample", help="Run sample only", action="store_true")
        subparser.add_argument("--dataversion", help="Specify a data version to resume")
        subparser.add_argument("--newversion",
                               help="Forces the creation of a new data version (If you don't specify this or " +
                                    "--dataversion, the latest version will be used. If there are no versions, a new one will be created.)",
                               action="store_true")

        for source_id, source_class in self.sources.items():
            for argument_definition in source_class.argument_definitions:
                subparser.add_argument('--' + argument_definition['name'], help=argument_definition['help'])

    def run_command(self, args):
        run = []

        if args.all and args.source:
            print("You need to either specify a source or use --all flag, not both.")
            quit(-1)

        if args.all:
            for source_id, source_class in self.sources.items():
                run.append({'id': source_id, 'source_class': source_class})
        elif args.source:
            for selected_source in args.source:
                if selected_source in self.sources:
                    run.append({'id': selected_source, 'source_class': self.sources[selected_source]})
                else:
                    logging.error("We can not find a source that you requested! You requested: %s" % selected_source)
                    quit(-1)

        if not run:
            logging.error("You have not specified anything to run! Try listing your sources names or flag --all")
            print("You can run:")
            for source_id, source_info in sorted(self.sources.items()):
                print(" - %s" % source_id)
            quit(-1)

        this_dir = os.path.dirname(os.path.realpath(__file__))
        base_dir = args.basedir or os.path.join(this_dir, "..", "..", "..", "data")
        remove_dir = False
        sample_mode = args.sample
        data_version = args.dataversion
        new_version = args.newversion

        logging.debug("We will run: ")
        for sourceInfo in run:
            logging.debug(" - %s" % sourceInfo['id'])
        if sample_mode:
            print("Sample mode is on!")
        else:
            print("Sample mode is off.")

        run_gather = True
        run_fetch = True
        run_store = True
        run_check = True
        if args.onlygather:
            run_fetch = False
            run_store = False
            run_check = False
        elif args.onlyfetch:
            run_gather = False
            run_store = False
            run_check = False
        elif args.onlystore:
            run_gather = False
            run_fetch = False
            run_check = False
        elif args.onlycheck:
            run_gather = False
            run_fetch = False
            run_store = False
        else:
            if args.ignoregather:
                run_gather = False
            if args.ignorefetch:
                run_fetch = False
            if args.ignorestore:
                run_store = False
            if args.ignorecheck:
                run_check = False

        if run_store or run_check:
            # If we are doing an operation that requires the database, try and initialise it now
            # so that errors are caught before we start
            ocdsdata.database.init()

        for source_info in run:

            instance = source_info['source_class'](base_dir,
                                                   remove_dir=remove_dir,
                                                   sample=sample_mode,
                                                   data_version=data_version,
                                                   new_version=new_version
                                                   )
            instance.set_arguments(args)

            logging.debug("Now running: %s (Output Dir: %s, Data Version: %s)" % (source_info['id'], instance.output_directory, instance.data_version))

            if run_gather:
                logging.debug(" - gathering ...")
                instance.run_gather()
            else:
                logging.debug(" - skipping gather.")
            if run_fetch:
                logging.debug(" - fetching ...")
                instance.run_fetch()
            else:
                logging.debug(" - skipping fetch.")
            if run_store:
                logging.debug(" - storing ...")
                instance.run_store()
            else:
                logging.debug(" - skipping store.")
            if run_check:
                logging.debug(" - checking ...")
                instance.run_check()
            else:
                logging.debug(" - skipping check.")
