from ocdskingfisher.collection_util import get_all_collections
import ocdskingfisher.cli.commands.base
import ocdskingfisher.sources_util
import os


class ListCollections(ocdskingfisher.cli.commands.base.CLICommand):
    command = 'list-collections'

    def configure_subparser(self, subparser):
        pass

    def run_command(self, args):

        this_dir = os.path.dirname(os.path.realpath(__file__))
        data_dir = os.path.join(this_dir, "..", "..", "..", "data")

        collections = get_all_collections(data_dir)

        print("{:5} {:4} {:40} {:20} {:5}".format(
            "DB-ID", "DISK", "SOURCE-ID", "DATA-VERSION", "SAMPLE"
        ))

        for collection in collections:
            print("{:5} {:4} {:40} {:20} {:5}".format(
                    (collection.database_id if collection.database_id else "-"),
                    ("Disk" if collection.on_disk else "-"),
                    collection.source_id[:40],
                    collection.data_version,
                    ("Sample" if collection.sample else "Full")
                ))
