import os
import json
import datetime

from .util import save_content
from . import database

DEFAULT_FETCH_FILE_DATA = {
    "publisher_name": None,
    "sample": False,
    "url": None,
    "metadata_creation_datetime": None,

    "gather_start_datetime": None,
    "gather_failure_exception": None,
    "gather_failure_datetime": None,
    "gather_finished_datetime": None,
    "gather_success": None,

    "file_status": {},

    "fetch_start_datetime": None,
    "fetch_finished_datetime": None,
    "fetch_success": None,

    "upload_start_datetime": None,
    "upload_error": None,
    "upload_success": None,
    "upload_finish_datetime": None,
}

DEFAULT_FILE_STATUS = {
    'url': None,
    'data_type': None,
    'gather_errors': None,

    'fetch_start_datetime': None,
    'fetch_errors': None,
    'fetch_finished_datetime': None,
    'fetch_success': None,

    "upload_start_datetime": None,
    "upload_error": None,
    "upload_finish_datetime": None,
    "upload_success": None,
}


"""Base class for defining OCDS publisher sources.

Defines the publisher name, the base URL source, methods to fetch and scrape the resources.
"""
class Source:
    publisher_name = None
    url = None
    output_directory = None
    source_id = None
    sample = False

    def __init__(self, base_dir, remove_dir=False, publisher_name=None, url=None, output_directory=None, sample=False):

        self.base_dir = base_dir
        self.sample = sample

        self.publisher_name = publisher_name or self.publisher_name
        if not self.publisher_name:
            raise AttributeError('A publisher name needs to be specified')
        self.output_directory = output_directory or self.output_directory or self.source_id
        if not self.output_directory:
            raise AttributeError('An output directory needs to be specified')

        self.url = url or self.url

        if self.sample and not self.output_directory.endswith('_sample'):
            self.output_directory += '_sample'

        self.full_directory = os.path.join(base_dir, self.output_directory)

        exists = os.path.exists(self.full_directory)

        if exists and remove_dir:
            os.rmdir(self.full_directory)
            exists = False

        if not exists:
            os.mkdir(self.full_directory)

        self.metadata_file = os.path.join(self.full_directory, '_fetch_metadata.json')
        metadata_exists = os.path.exists(self.metadata_file)
        if not metadata_exists:
            self.save_metadata(DEFAULT_FETCH_FILE_DATA)
        metadata = self.get_metadata()
        metadata['publisher_name'] = self.publisher_name
        metadata['sample'] = self.sample
        metadata['url'] = self.url
        metadata['metadata_creation_datetime'] = str(datetime.datetime.utcnow())
        self.save_metadata(metadata)

    def get_metadata(self):
        with open(self.metadata_file) as f:
            return json.load(f)

    def save_metadata(self, metadata):
        with open(self.metadata_file, 'w+') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)


    """Returns an array with objects for each url.

    The return objects includes url,filename,type and more."""
    def gather_all_download_urls(self):
        raise NotImplementedError()

    def run_gather(self):
        metadata = self.get_metadata()

        if metadata['gather_success']:
            return

        #reset gather data
        for key in list(metadata):
            if key.startswith('gather_'):
                metadata[key] = None

        metadata['gather_start_datetime'] = str(datetime.datetime.utcnow())
        metadata['download_status'] = {}
        self.save_metadata(metadata)

        failed = False
        try:
            for info in self.gather_all_download_urls():
                file_status = DEFAULT_FILE_STATUS.copy()
                file_status['url'] = info['url']
                file_status['data_type'] = info['data_type']
                file_status['gather_errors'] = info['errors']

                metadata['file_status'][info['filename']] = file_status

                if info['errors'] and not metadata['gather_failure_datetime']:
                    metadata['gather_failure_datetime'] = str(datetime.datetime.utcnow())
                    failed = True
                self.save_metadata(metadata)
        except Exception as e:
            metadata['gather_failure_exception'] = repr(e)
            metadata['gather_failure_datetime'] = str(datetime.datetime.utcnow())
            metadata['gather_success'] = False
            metadata['gather_finished_datetime'] = str(datetime.datetime.utcnow())
            self.save_metadata(metadata)
            failed = True

        metadata['gather_success'] = not failed
        metadata['gather_finished_datetime'] = str(datetime.datetime.utcnow())
        self.save_metadata(metadata)

    def run_fetch(self):
        metadata = self.get_metadata()

        if metadata['fetch_success']:
            return

        if not metadata['gather_success']:
            raise Exception('Can not run fetch without a successful gather')

        for key in list(metadata):
            if key.startswith('fetch_'):
                metadata[key] = None

        metadata['fetch_start_datetime'] = str(datetime.datetime.utcnow())
        self.save_metadata(metadata)

        failed = False
        stop = False

        while not stop:
            stop = True
            # List() is needed here to copy the array of keys, so that if they change inside the loop it doesn't crash.
            for file_name in list(metadata['file_status'].keys()):

                data = metadata['file_status'][file_name]

                if data['fetch_success']:
                    continue

                for key in list(data):
                    if key.startswith('fetch_'):
                        data[key] = None

                data['fetch_start_datetime'] = str(datetime.datetime.utcnow())
                data['fetch_errors'] = []

                self.save_metadata(metadata)
                try:
                    to_add_list, errors = self.save_url(file_name, data, os.path.join(self.full_directory, file_name))
                    if to_add_list:
                        stop = False
                        for info in to_add_list:
                            file_status = DEFAULT_FILE_STATUS.copy()
                            file_status['url'] = info['url']
                            file_status['data_type'] = info['data_type']
                            file_status['gather_errors'] = info['errors']

                            metadata['file_status'][info['filename']] = file_status

                except Exception as e:
                    errors = [repr(e)]

                if errors:
                    data['fetch_errors'] = errors
                    data['fetch_success'] = False
                    failed = True
                else:
                    data['fetch_success'] = True
                    data['fetch_errors'] = []

                data['fetch_finished_datetime'] = str(datetime.datetime.utcnow())
                self.save_metadata(metadata)

        metadata['fetch_success'] = not failed
        metadata['fetch_finished_datetime'] = str(datetime.datetime.utcnow())
        self.save_metadata(metadata)

    def _upload_abort(self, error_msg, metadata, data):
        data['upload_error'] = error_msg
        metadata['upload_error'] = error_msg
        metadata['upload_success'] = False
        metadata['upload_finished_datetime'] = str(datetime.datetime.utcnow())
        database.delete_releases(self.source_id)
        database.delete_records(self.source_id)
        self.save_metadata(metadata)

    """Uploads the fetched data as record rows to the Database"""
    def run_upload(self):
        metadata = self.get_metadata()

        if metadata['upload_success']:
            return

        if not metadata['fetch_success']:
            raise Exception('Can not run upload without a successful fetch')

        for key in list(metadata):
            if key.startswith('upload_'):
                metadata[key] = None

        for file_name, data in metadata['file_status'].items():
            for key in list(data):
                if key.startswith('upload_'):
                    data[key] = None

        metadata['upload_start_datetime'] = str(datetime.datetime.utcnow())
        self.save_metadata(metadata)

        for file_name, data in metadata['file_status'].items():

            if data['data_type'].startswith('meta'):
                continue

            data['upload_start_datetime'] = str(datetime.datetime.utcnow())

            self.save_metadata(metadata)

            try:
                with open(os.path.join(self.full_directory, file_name)) as f:
                    json_data = json.load(f)
            except Exception as e:
                error_msg = 'Unable to load JSON from disk ({}): {}'.format(file_name, repr(e))
                self._upload_abort(error_msg, metadata, data)
                return

            error_msg = ''
            if not isinstance(json_data, dict):
                error_msg = "Can not process data in file {} as JSON is not an object".format(file_name)

            if data['data_type'] == 'release_package':
                if 'releases' not in json_data:
                    error_msg = "Release list not found in file {}".format(file_name)
                elif not isinstance(json_data['releases'], list):
                    error_msg = "Release list which is not a list found in file {}".format(file_name)
                data_list = json_data['releases']
            elif data['data_type'] == 'record_package':
                if 'records' not in json_data:
                    error_msg = "Record list not found in file {}".format(file_name)
                elif not isinstance(json_data['records'], list):
                    error_msg = "Record list which is not a list found in file {}".format(file_name)
                data_list = json_data['records']
            else:
                error_msg = "data_type not release_package or record_package"

            if error_msg:
                self._upload_abort(error_msg, metadata, data)
                return

            package_data = {}
            for key, value in json_data.items():
                if key not in ('releases', 'records'):
                    package_data[key] = value

            data_for_database = []
            for row in data_list:
                if not isinstance(row, dict):
                    error_msg = "Row in data is not a object {}".format(file_name)
                    self._upload_abort(error_msg, metadata, data)
                    return

                row_in_database = {
                    "source_id": self.source_id,
                    "sample": self.sample,
                    "file": file_name,
                    "publisher_name": self.publisher_name,
                    "url": self.url,
                    "package_data": package_data
                }

                if data['data_type'] == 'record_package':
                    row_in_database['record'] = row
                    row_in_database['ocid'] = row.get('ocid')

                if data['data_type'] == 'release_package':
                    row_in_database['release'] = row
                    row_in_database['ocid'] = row.get('ocid')
                    row_in_database['release_id'] = row.get('id')

                data_for_database.append(row_in_database)

            if data['data_type'] == 'record_package':
                database.insert_records(data_for_database)
            else:
                database.insert_releases(data_for_database)

            data['upload_finished_datetime'] = str(datetime.datetime.utcnow())
            data['upload_success'] = True
            self.save_metadata(metadata)

        metadata['upload_success'] = True
        metadata['upload_finished_datetime'] = str(datetime.datetime.utcnow())
        self.save_metadata(metadata)

    def save_url(self, file_name, data, file_path):
        return [], save_content(data['url'], file_path)

    """Gather and Fetch all data from this publisher."""
    def run_all(self):
        self.run_gather()
        self.run_fetch()
