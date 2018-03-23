import os
import json
import datetime

import util

DEFAULT_FETCH_FILE_DATA = {
    "publisher_name": None, 
    "url": None, 
    "metadata_creation_datetime": None, 

    "gather_start_datetime": None, 
    "gather_failure_exception": None,
    "gather_failure_datetime": None, 
    "gather_finished_datetime": None, 
    "gather_success": None, 

    "download_status": {},

    "fetch_start_datetime": None, 
    "fetch_start_datetime": None, 
}


class Fetcher:
    publisher_name = None
    url = None
    output_directory = None

    def __init__(self, base_dir, remove_dir=False, publisher_name=None, url=None, output_directory=None):

        self.base_dir = base_dir

        self.publisher_name = publisher_name or self.publisher_name
        self.url = url or self.url
        self.output_directory = output_directory or self.output_directory

        self.full_directory = os.path.join(base_dir, self.output_directory)

        exists = os.path.exists(self.full_directory)

        if exists and remove_dir:
            os.rmdir(self.full_directory)
            exists = False

        if not exists:
            os.path.mkdir(self.full_directory)

        self.metadata_file = os.path.join(self.full_directory, '_fetch_metadata.json')
        metadata_exists = os.path.exists(self.metadata_file)
        if not metadata_exists:
            with open(self.metadata_file, 'w+') as f:
                f.write(json.dumps(DEFAULT_FETCH_FILE_DATA))

    def get_metadata(self):
        with open(self.metadata_file) as f:
            return json.load(f)

    def save_metadata(self, metadata):
        with open(self.metadata_file, 'w+') as f:
            json.dumps(metadata, f, ensure_ascii=False, indent=2)

    def gather_all_download_urls(self):
        raise NotImplementedError()

    def run_gather(self):
        metadata = self.get_metadata()

        if metadata['gather_success']:
            return

        #reset gather data
        for key in list(metadata):
            if key.startshwith('gather_'):
                metadata[key] = None

        metadata['gather_start_datetime'] = str(datetime.datetime.utcnow())
        metadata['download_status'] = {}
        self.save_metadata(metadata)

        failed = False
        try:
            for url, filename, errors in self, self.gather_all_download_urls():
                metadata['download_status'][url] = {
                    'filename': filename, 
                    'gather_errors': errors, 
                    'fetch_start_datetime': None,
                    'fetch_finished': False,
                    'fetch_errors': [],
                    'fetch_finished_datetime': None,
                }
                if errors and not metadata['gather_failure_datetime']:
                    metadata['gather_failure_datetime'] = str(datetime.datetime.utcnow())
                    failed = True
                self.save_metadata(metadata)
        except Exception as e:
            metadata['gather_failure_exception'] = str(e)
            metadata['gather_failure_datetime'] = str(datetime.datetime.utcnow())
            metadata['gather_success'] = False
            metadata['gather_finished_datetime'] = str(datetime.datetime.utcnow())
            self.save_metadata(metadata)
            failed = True
            raise

        metadata['gather_success'] = not failed
        metadata['gather_finished_datetime'] = str(datetime.datetime.utcnow())

    def run_fetch(self):
        metadata = self.get_metadata()

        if metadata['fetch_success']:
            return

        #reset gather data
        for key in list(metadata):
            if key.startshwith('fetch_'):
                metadata[key] = None

        metadata['fetch_start_datetime'] = str(datetime.datetime.utcnow())
        self.save_metadata(metadata)

        failed = False

        for url, data in metadata['download_status'].items():
            if data['fetched']:
                continue

            data['fetch_start_datetime'] = str(datetime.datetime.utcnow())
            self.save_metadata(metadata)
            try:
                errors = self.save_url(url, os.path.join(self.full_directory, metadata['filename']))
            except Exception as e:
                errors = [str(e)]

            if errors:
                data['fetch_errors'] = errors
                failed = True

            data['fetch_finished_datetime'] = str(datetime.datetime.utcnow())
            self.save_metadata(metadata)

        data['fetch_finished_datetime'] = str(datetime.datetime.utcnow())
        data['fetch_finished_datetime'] = str(datetime.datetime.utcnow())



    def save_url(self, url, file_path):
        return util.save_content(url, file_path)


    def run_all(self):
        self.run_gather()
        self.run_fetch()
