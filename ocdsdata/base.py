import os
import json
import datetime

from .util import save_content
from . import database

DEFAULT_FETCH_FILE_DATA = {
    "publisher_name": None,
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


class Source:
    publisher_name = None
    url = None
    output_directory = None
    source_id = None

    def __init__(self, base_dir, remove_dir=False, publisher_name=None, url=None, output_directory=None):

        self.base_dir = base_dir

        self.publisher_name = publisher_name or self.publisher_name
        if not self.publisher_name:
            raise AttributeError('A publisher name needs to be specified')
        self.output_directory = output_directory or self.output_directory or self.source_id
        if not self.output_directory:
            raise AttributeError('An output directory needs to be specified')

        self.url = url or self.url

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
        metadata['url'] = self.url
        metadata['metadata_creation_datetime'] = str(datetime.datetime.utcnow())
        self.save_metadata(metadata)

    def get_metadata(self):
        with open(self.metadata_file) as f:
            return json.load(f)

    def save_metadata(self, metadata):
        with open(self.metadata_file, 'w+') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

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
            for url, filename, data_type, errors in self.gather_all_download_urls():
                metadata['file_status'][filename] = {
                    'url': url,
                    'data_type': data_type,
                    'gather_errors': errors,

                    'fetch_start_datetime': None,
                    'fetch_errors': None,
                    'fetch_finished_datetime': None,
                    'fetch_success': None,

                    "upload_start_datetime": None,
                    "upload_error": None,
                    "upload_finish_datetime": None,
                    "upload_success": None,
                }
                if errors and not metadata['gather_failure_datetime']:
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

        for file_name, data in metadata['file_status'].items():
            if data['fetch_success']:
                continue

            for key in list(data):
                if key.startswith('fetch_'):
                    data[key] = None

            data['fetch_start_datetime'] = str(datetime.datetime.utcnow())
            data['fetch_errors'] = []

            self.save_metadata(metadata)
            try:
                errors = self.save_url(data['url'], os.path.join(self.full_directory, file_name))
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

            data['upload_start_datetime'] = str(datetime.datetime.utcnow())

            self.save_metadata(metadata)
            
            try:
                with file(os.path.join(self.full_directory, file_name)) as f:
                    json_data = json.load(f)
            except Exception as e:
                data['upload_error'] = 'Unable to load JSON from disk: ()' + repr(e)
                metadata['upload_error'] = ['Unable to load JSON from disk ({}): {}' + repr(e)]
                metadata['upload_success'] = False
                metadata['upload_finished_datetime'] = str(datetime.datetime.utcnow())
                self.save_metadata(metadata)
                database.delete_releases(self.output_directory)
                return

            error_msg = ''

            data['upload_finished_datetime'] = str(datetime.datetime.utcnow())
            self.save_metadata(metadata)

        metadata['upload_success'] = True
        metadata['upload_finished_datetime'] = str(datetime.datetime.utcnow())
        self.save_metadata(metadata)


    def save_url(self, url, file_path):
        return save_content(url, file_path)

    def run_all(self):
        self.run_gather()
        self.run_fetch()
