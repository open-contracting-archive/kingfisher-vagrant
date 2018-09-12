import ocdskingfisher.database
import ocdskingfisher.sources_util
import os


class Collection:

    def __init__(self, source_id=None, data_version=None, sample=None, on_disk=None, database_id=None):
        self.source_id = source_id
        self.data_version = data_version
        self.sample = sample
        self.database_id = database_id
        self.on_disk = on_disk


def get_all_collections(config):
    out = []

    # Load from database
    for result in ocdskingfisher.database.get_all_collections():
        out.append(Collection(
            database_id=result['id'],
            source_id=result['source_id'],
            data_version=result['data_version'],
            sample=result['sample'],
        ))

    # Load from disk
    for sample in [True, False]:
        for key in ocdskingfisher.sources_util.gather_sources().keys():
            directory = os.path.join(config.data_dir, key + ("_sample" if sample else ""))
            if os.path.isdir(directory):
                for version in os.listdir(directory):
                    if os.path.isdir(os.path.join(directory, version)) and \
                            os.path.isfile(os.path.join(directory, version, "metadb.sqlite3")):
                        _get_all_collections_disk_collection_found(
                            source_id=key,
                            data_version=version,
                            sample=sample,
                            out=out,
                        )

    # Return results
    return out


def _get_all_collections_disk_collection_found(source_id, data_version, sample, out):

    for existing in out:
        if existing.source_id == source_id and existing.data_version == data_version and existing.sample == sample:
            existing.on_disk = True
            return

    out.append(Collection(
        source_id=source_id,
        data_version=data_version,
        sample=sample,
        on_disk=True
    ))
