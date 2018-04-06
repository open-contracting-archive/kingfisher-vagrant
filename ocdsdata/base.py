import os
import sys
import json
import datetime
import traceback

from .util import save_content
from . import database
from .metadata_db import MetadataDB

"""Base class for defining OCDS publisher sources.

Defines the publisher name, the base URL source, methods to fetch and scrape the resources.
"""
class Source:
    publisher_name = None
    url = None
    output_directory = None
    source_id = None
    sample = False
    data_version = None

    def __init__(self, base_dir, remove_dir=False, publisher_name=None, url=None, output_directory=None, sample=False, data_version=None):

        self.base_dir = base_dir
        self.sample = sample

        self.data_version = data_version or self.data_version or datetime.datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')

        self.publisher_name = publisher_name or self.publisher_name
        if not self.publisher_name:
            raise AttributeError('A publisher name needs to be specified')
        self.output_directory = output_directory or self.output_directory or self.source_id
        if not self.output_directory:
            raise AttributeError('An output directory needs to be specified')

        self.url = url or self.url

        if self.sample and not self.output_directory.endswith('_sample'):
            self.output_directory += '_sample'

        self.full_directory = os.path.join(base_dir, self.output_directory, self.data_version)

        exists = os.path.exists(self.full_directory)

        if exists and remove_dir:
            os.rmdir(self.full_directory)
            exists = False

        if not exists:
            os.makedirs(self.full_directory)

        self.metadata_db = MetadataDB(self.full_directory)

        self.metadata_db.create_session_metadata(
            publisher_name = self.publisher_name,
            sample = self.sample,
            url = self.url,
            data_version = self.data_version
        )

    """Returns an array with objects for each url.

    The return objects includes url,filename,type and more."""
    def gather_all_download_urls(self):
        raise NotImplementedError()

    def run_gather(self):

        self.metadata_db.update_session_gather_start()

        failed = False
        try:
            for info in self.gather_all_download_urls():
                self.metadata_db.add_filestatus(**info)
                if info['errors']:
                    failed = True
        except Exception as e:
            error = repr(e)
            stacktrace = traceback.format_exception(*sys.exc_info())
            self.metadata_db.update_session_gather_end(False, error, stacktrace)
            return

        self.metadata_db.update_session_gather_end(not failed, None, None)

    def run_fetch(self):
        metadata = self.metadata_db.get_session()

        if metadata['fetch_success']:
            return

        if not metadata['gather_success']:
            raise Exception('Can not run fetch without a successful gather')

        self.metadata_db.update_session_fetch_start()

        failed = False
        stop = False

        while not stop:
            stop = True
            for data in self.metadata_db.list_filestatus():

                if data['fetch_success']:
                    continue

                self.metadata_db.update_filestatus_fetch_start(data['filename'])
                try:
                    to_add_list, errors = self.save_url(data['filename'], data, os.path.join(self.full_directory, data['filename']))
                    if to_add_list:
                        stop = False
                        for info in to_add_list:
                            self.metadata_db.add_filestatus(**info)

                except Exception as e:
                    errors = [repr(e)]

                if errors:
                    self.metadata_db.update_filestatus_fetch_end(data['filename'], False, str(errors))
                    failed = True
                else:
                    self.metadata_db.update_filestatus_fetch_end(data['filename'], True)

        self.metadata_db.update_session_fetch_end(not failed) ## No ERrors Passed here?

    """Uploads the fetched data as record rows to the Database"""
    def run_store(self):
        metadata = self.metadata_db.get_session()

        # We should check if this store has already been done.
        # This needs to be done in the Postgres database.#
        # TODO
        #if metadata['store_success']:
        #    return

        if not metadata['fetch_success']:
            raise Exception('Can not run store without a successful fetch')

        for data in self.metadata_db.list_filestatus():

            if data['data_type'].startswith('meta'):
                continue

            try:
                with open(os.path.join(self.full_directory, data['filename']),
                          encoding=data['encoding']) as f:
                    json_data = json.load(f)
            except Exception as e:
                ## TODO better way of dealing with this?
                raise e
                return

            objects_list = []
            if data['data_type'] == 'record_package_list_in_results':
                objects_list.extend(json_data['results'])
            elif data['data_type'] == 'release_package_list_in_results':
                objects_list.extend(json_data['results'])
            elif data['data_type'] == 'record_package_list' or data['data_type'] == 'release_package_list':
                objects_list.extend(json_data)
            else:
                objects_list.append(json_data)

            for json_data in objects_list:
                error_msg = ''
                if not isinstance(json_data, dict):
                    error_msg = "Can not process data in file {} as JSON is not an object".format(data['filename'])

                if data['data_type'] == 'release_package' or data['data_type'] == 'release_package_list_in_results' or data['data_type'] == 'release_package_list' :
                    if 'releases' not in json_data:
                        error_msg = "Release list not found in file {}".format(data['filename'])
                    elif not isinstance(json_data['releases'], list):
                        error_msg = "Release list which is not a list found in file {}".format(data['filename'])
                    data_list = json_data['releases']
                elif data['data_type'] == 'record_package' or data['data_type'] == 'record_package_list_in_results' or data['data_type'] == 'record_package_list':
                    if 'records' not in json_data:
                        error_msg = "Record list not found in file {}".format(data['filename'])
                    elif not isinstance(json_data['records'], list):
                        error_msg = "Record list which is not a list found in file {}".format(data['filename'])
                    data_list = json_data['records']
                else:
                    error_msg = "data_type not a known type"

                if error_msg:
                    self._store_abort(error_msg, metadata, data)
                    return
                package_data = {}
                for key, value in json_data.items():
                    if key not in ('releases', 'records'):
                        package_data[key] = value

                data_for_database = []
                for row in data_list:
                    if not isinstance(row, dict):
                        error_msg = "Row in data is not a object {}".format(data['filename'])
                        self._store_abort(error_msg, metadata, data)
                        return

                    row_in_database = {
                        "source_id": self.source_id,
                        "sample": self.sample,
                        "file": data['filename'],
                        "publisher_name": self.publisher_name,
                        "url": self.url,
                        "package_data": package_data,
                        "data_version": self.data_version,
                    }

                    if data['data_type'] == 'record_package' or data['data_type'] == 'record_package_list_in_results' or data['data_type'] == 'record_package_list':
                        row_in_database['record'] = row
                        row_in_database['ocid'] = row.get('ocid')

                    if data['data_type'] == 'release_package' or data['data_type'] == 'release_package_list_in_results' or data['data_type'] == 'release_package_list':
                        row_in_database['release'] = row
                        row_in_database['ocid'] = row.get('ocid')
                        row_in_database['release_id'] = row.get('id')

                    data_for_database.append(row_in_database)

                if data['data_type'] == 'record_package' or data['data_type'] == 'record_package_list_in_results' or data['data_type'] == 'record_package_list':
                    database.insert_records(data_for_database)
                else:
                    database.insert_releases(data_for_database)

    def save_url(self, file_name, data, file_path):
        return [], save_content(data['url'], file_path)

    """Gather and Fetch all data from this publisher."""
    def run_all(self):
        self.run_gather()
        self.run_fetch()
