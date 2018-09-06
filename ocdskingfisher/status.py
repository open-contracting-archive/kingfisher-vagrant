import os
from ocdskingfisher.metadata_db import MetadataDB
from ocdskingfisher import database


class SourceStatus:

    def __init__(self, base_dir, source_id, output_directory=None, sample=False, data_version=None):

        self.base_dir = base_dir
        self.source_id = source_id
        self.sample = sample

        # Make sure the output directory is fully specified, including sample bit (if applicable)
        self.output_directory = output_directory or source_id
        if not self.output_directory:
            raise AttributeError('An output directory needs to be specified')

        if self.sample and not self.output_directory.endswith('_sample'):
            self.output_directory += '_sample'

        # Load all versions if possible, pick an existing one or set a new one.
        all_versions = sorted(os.listdir(os.path.join(base_dir, self.output_directory)), reverse=True)\
            if os.path.exists(os.path.join(base_dir, self.output_directory)) else []

        if data_version and data_version in all_versions:  # Version specified is valid
            self.data_version = data_version
        elif data_version:   # Version specified is invalid!
            raise AttributeError('A version was specified that does not exist')
        elif len(all_versions) > 0:  # Get the latest version to resume
            self.data_version = all_versions[0]
        else:  # Should not happen...
            raise AttributeError('The source and/or version is unavailable on the output directory')

        # Build full directory, make sure it exists
        self.full_directory = os.path.join(base_dir, self.output_directory, self.data_version)
        if not os.path.exists(self.full_directory):
            raise AttributeError('Full Directory does not exist!')

        # Misc
        self.metadata_db = MetadataDB(self.full_directory)

    def is_gather_finished(self):
        metadata = self.metadata_db.get_session()
        return bool(metadata['gather_finished_datetime'])

    def get_gather_progress_as_text(self):

        out = []
        metadata = self.metadata_db.get_session()

        if metadata['gather_start_datetime']:
            out.append("Started " + metadata['gather_start_datetime'].strftime("%c"))

        return "\n".join(out)

    def is_fetch_finished(self):
        metadata = self.metadata_db.get_session()
        return bool(metadata['fetch_finished_datetime'])

    def get_fetch_progress_as_text(self):

        file_statuses = self.metadata_db.list_filestatus()
        count_finished = 0
        current_out = []

        for file_status in file_statuses:
            if file_status['fetch_finished_datetime'] is not None:
                count_finished += 1

            if file_status['fetch_start_datetime'] and file_status['fetch_finished_datetime'] is None:
                current_out.append("Filename: " + file_status['filename'])
                current_out.append("URL: " + file_status['url'])
                current_out.append("Data Type: " + file_status['data_type'])
                current_out.append("Encoding: " + file_status['encoding'])
                current_out.append("Priority: " + str(file_status['priority']))
                current_out.append("Started: " + file_status['fetch_start_datetime'].strftime("%c"))

        out = "Finished " + str(count_finished) + " out of " + str(len(file_statuses)) + " files.\n"
        if current_out:
            return out + "\nIn Progress:\n" + "\n".join(current_out)
        else:
            return out

    def is_store_finished(self):
        return database.is_store_done(self.source_id, self.data_version, self.sample)

    def get_store_progress_as_text(self):
        return 'Store is in progress'

    def is_check_finished(self):
        source_session_id = database.get_id_of_store(self.source_id, self.data_version, self.sample)
        return database.is_check_done(source_session_id)

    def get_check_progress_as_text(self):
        return 'Check is in progress'
