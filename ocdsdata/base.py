import os
import sys
import json
import datetime
import traceback

from ocdsdata.util import save_content
from ocdsdata.checks import check_file
from ocdsdata import database
from ocdsdata.metadata_db import MetadataDB

"""Base class for defining OCDS publisher sources.

Each source should extend this class and add some variables and implement a few methods.

method gather_all_download_urls - this is called once at the start and should return a list of files to download.

method save_url - this is called once per file to download. You may not need to implement this for a simple source, as
the default implementation may be good enough. It returns an instance of Source.SaveURLResult which can hold errors,
warnings, and new files to download.

Files to be downloaded are described by a dict. Both gather_all_download_urls and Source.SaveURLResult.additional_files
use the same structure. The keys are:

  *  filename - the name of the file that will be saved locally. These need to be unique per source.
  *  url - the URL to download.
  *  data_type - the type of the file. See below.
  *  encoding - encoding of the file. Optional, defaults to utf-8.
  *  priority - higher numbers will be fetched first, defaults to 1.

The data_type should be one of the following options:

  *  record_package - the file is a record package.
  *  release_package - the file is a release package.
  *  record_package_list - the file is a list of record packages. eg
     [  { record-package-1 } , { record-package-2 } ]
  *  release_package_list - see last entry, but release packages.
  *  record_package_list_in_results - the file is a list of record packages in the results attribute. eg
     { 'results': [  { record-package-1 } , { record-package-2 } ]  }
  *  release_package_list_in_results - see last entry, but release packages.
  *  meta* - files with a type that starts with meta are fetched as normal, but then ignored while storing to the database.
     You may need these files to work out more files to download. See the ukraine source for an example.
"""


class Source:
    publisher_name = None
    url = None
    output_directory = None
    source_id = None
    sample = False
    data_version = None
    """It is possible to pass extra arguments.

    This specifies a list of the extra arguments possible. Each item in the list should be a dict with the keys:
      *  name - a name compatible with argparse. Names should be unique across all sources, so include a prefix of some kind.
      *  help - a help string for argparse
    """
    argument_definitions = []

    def __init__(self, base_dir, remove_dir=False, publisher_name=None, url=None, output_directory=None, sample=False, data_version=None, new_version=False):

        self.base_dir = base_dir
        self.sample = sample

        self.publisher_name = publisher_name or self.publisher_name
        if not self.publisher_name:
            raise AttributeError('A publisher name needs to be specified')

        # Make sure the output directory is fully specified, including sample bit (if applicable)
        self.output_directory = output_directory or self.output_directory or self.source_id
        if not self.output_directory:
            raise AttributeError('An output directory needs to be specified')

        if self.sample and not self.output_directory.endswith('_sample'):
            self.output_directory += '_sample'

        # Load all versions if possible, pick an existing one or set a new one.
        all_versions = sorted(os.listdir(os.path.join(base_dir, self.output_directory)), reverse=True)\
            if os.path.exists(os.path.join(base_dir, self.output_directory)) else []

        if self.data_version:
            pass
        elif data_version and data_version in all_versions:  # Version specified is valid
            self.data_version = data_version
        elif data_version:   # Version specified is invalid!
            raise AttributeError('A version was specified that does not exist')
        elif new_version or len(all_versions) == 0:  # New Version
            self.data_version = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
        elif len(all_versions) > 0:  # Get the latest version to resume
            self.data_version = all_versions[0]
        else:  # Should not happen...
            raise AttributeError('The version is unavailable on the output directory')

        # Build full directory, make sure it exists
        self.full_directory = os.path.join(base_dir, self.output_directory, self.data_version)

        exists = os.path.exists(self.full_directory)

        try:
            if exists and remove_dir:
                os.rmdir(self.full_directory)
                exists = False

            if not exists:
                os.makedirs(self.full_directory)
        except OSError:
            raise RuntimeError("Error: Write permission is needed on the directory specified (or project dir). %s" % self.full_directory)

        # Misc

        self.url = url or self.url

        self.metadata_db = MetadataDB(self.full_directory)

        self.metadata_db.create_session_metadata(
            publisher_name=self.publisher_name,
            sample=self.sample,
            url=self.url,
            data_version=self.data_version
        )

    """Returns an array with objects for each url.

    The return objects includes url,filename,type and more."""
    def gather_all_download_urls(self):
        raise NotImplementedError()

    def set_arguments(self, arguments):
        pass

    def run_gather(self):
        metadata = self.metadata_db.get_session()

        if metadata['gather_success']:
            return

        self.metadata_db.update_session_gather_start()

        try:
            for info in self.gather_all_download_urls():
                if self.metadata_db.has_filestatus_filename(info['filename']):
                    if not self.metadata_db.compare_filestatus_to_database(info):
                        raise Exception("Tried to add the file " + info['filename'] +
                                        " but it clashed with a file already in the list!")
                else:
                    self.metadata_db.add_filestatus(info)
        except Exception as e:
            error = repr(e)
            stacktrace = traceback.format_exception(*sys.exc_info())
            self.metadata_db.update_session_gather_end(False, error, stacktrace)
            return

        self.metadata_db.update_session_gather_end(True, None, None)

    def run_fetch(self):
        metadata = self.metadata_db.get_session()

        if metadata['fetch_success']:
            return

        if not metadata['gather_success']:
            msg = 'Can not run fetch without a successful gather!'
            if metadata['gather_errors']:
                msg += ' Gather errors: ' + metadata['gather_errors']
            raise Exception(msg)

        self.metadata_db.update_session_fetch_start()

        data = self.metadata_db.get_next_filestatus_to_fetch()
        while data:
            self.metadata_db.update_filestatus_fetch_start(data['filename'])
            try:
                response = self.save_url(data['filename'], data, os.path.join(self.full_directory, data['filename']))
                if response.additional_files:
                    for info in response.additional_files:
                        if self.metadata_db.has_filestatus_filename(info['filename']):
                            if not self.metadata_db.compare_filestatus_to_database(info):
                                response.errors.append("Tried to add the file " + info['filename'] +
                                                       " but it clashed with a file already in the list!")
                        else:
                            self.metadata_db.add_filestatus(info)
                self.metadata_db.update_filestatus_fetch_end(data['filename'], response.errors, response.warnings)

            except Exception as e:
                self.metadata_db.update_filestatus_fetch_end(data['filename'], [repr(e)])

            data = self.metadata_db.get_next_filestatus_to_fetch()

        self.metadata_db.update_session_fetch_end()

    """Uploads the fetched data as record rows to the Database"""
    def run_store(self):
        metadata = self.metadata_db.get_session()

        if not metadata['fetch_success']:
            raise Exception('Can not run store without a successful fetch')

        if database.is_store_done(self.source_id, self.data_version, self.sample):
            return

        source_session_id = database.start_store(self.source_id, self.data_version, self.sample, self.metadata_db)

        for data in self.metadata_db.list_filestatus():

            if data['data_type'].startswith('meta'):
                continue

            if database.is_store_file_done(source_session_id, data):
                continue

            with database.add_file(source_session_id, data) as database_file:

                try:
                    with open(os.path.join(self.full_directory, data['filename']),
                              encoding=data['encoding']) as f:
                        file_json_data = json.load(f)
                except Exception as e:
                    # TODO better way of dealing with this?
                    raise e
                    return

                objects_list = []
                if data['data_type'] == 'record_package_list_in_results':
                    objects_list.extend(file_json_data['results'])
                elif data['data_type'] == 'release_package_list_in_results':
                    objects_list.extend(file_json_data['results'])
                elif data['data_type'] == 'record_package_list' or data['data_type'] == 'release_package_list':
                    objects_list.extend(file_json_data)
                else:
                    objects_list.append(file_json_data)

                del file_json_data

                for json_data in objects_list:
                    error_msg = ''
                    if not isinstance(json_data, dict):
                        error_msg = "Can not process data in file {} as JSON is not an object".format(data['filename'])

                    if data['data_type'] == 'release_package' or \
                            data['data_type'] == 'release_package_list_in_results' or \
                            data['data_type'] == 'release_package_list':
                        if 'releases' not in json_data:
                            error_msg = "Release list not found in file {}".format(data['filename'])
                        elif not isinstance(json_data['releases'], list):
                            error_msg = "Release list which is not a list found in file {}".format(data['filename'])
                        data_list = json_data['releases']
                    elif data['data_type'] == 'record_package' or \
                            data['data_type'] == 'record_package_list_in_results' or \
                            data['data_type'] == 'record_package_list':
                        if 'records' not in json_data:
                            error_msg = "Record list not found in file {}".format(data['filename'])
                        elif not isinstance(json_data['records'], list):
                            error_msg = "Record list which is not a list found in file {}".format(data['filename'])
                        data_list = json_data['records']
                    else:
                        error_msg = "data_type not a known type"

                    if error_msg:
                        raise Exception(error_msg)
                    package_data = {}
                    for key, value in json_data.items():
                        if key not in ('releases', 'records'):
                            package_data[key] = value

                    for row in data_list:
                        if not isinstance(row, dict):
                            error_msg = "Row in data is not a object {}".format(data['filename'])
                            raise Exception(error_msg)

                        if data['data_type'] == 'record_package' or \
                                data['data_type'] == 'record_package_list_in_results' or \
                                data['data_type'] == 'record_package_list':
                            database_file.insert_record(row, package_data)
                        else:
                            database_file.insert_release(row, package_data)

        database.end_store(source_session_id)

    def save_url(self, file_name, data, file_path):
        save_content_response = save_content(data['url'], file_path)
        return self.SaveUrlResult(errors=save_content_response.errors, warnings=save_content_response.warnings)

    class SaveUrlResult:
        def __init__(self, additional_files=[], errors=[], warnings=[]):
            self.additional_files = additional_files
            self.errors = errors
            self.warnings = warnings

    def run_check(self):
        if not database.is_store_done(self.source_id, self.data_version, self.sample):
            raise Exception('Can not run check without a successful store')

        source_session_id = database.get_id_of_store(self.source_id, self.data_version, self.sample)

        for data in self.metadata_db.list_filestatus():

            if data['data_type'].startswith('meta'):
                continue

            check_file(source_session_id, data)

    """Gather, Fetch, Store and Check data from this publisher."""
    def run_all(self):
        self.run_gather()
        self.run_fetch()
        self.run_store()
        self.run_check()
