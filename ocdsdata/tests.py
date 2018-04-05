from os.path import join, exists
import tempfile

import pytest

from .base import Source
from . import util
from . import database
from ocdsdata.metadata_db import MetadataDB

#Monkey patch to make tests run a lot faster
util.RETRY_TIME = 0.1

class Basic(Source):
    publisher_name = 'test'
    url = 'test_url'
    source_id = 'test'
    data_version = 'v1'

    def gather_all_download_urls(self):
        yield {'url': 'https://raw.githubusercontent.com/open-contracting/sample-data/5bcbfcf48bf6e6599194b8acae61e2c6e8fb5009/fictional-example/1.1/ocds-213czf-000-00001-02-tender.json',
               'filename': 'file1.json',
               'data_type': 'releases',
               'errors': []}

def test_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = Basic(tmpdir)
        metadata_file = join(tmpdir, 'test', 'v1', '_fetch_metadata.json')
        assert exists(metadata_file)

        with MetadataDB(join(tmpdir, 'test', 'v1')) as metadata_db
            data = metadata_db.get_dict()
            assert data['publisher_name'] == 'test'
            assert data['url'] == 'test_url'
            assert data['metadata_creation_datetime']

        fetcher.run_gather()
        with MetadataDB(join(tmpdir, 'test', 'v1')) as metadata_db
            data = metadata_db.get_dict()
            assert data['gather_start_datetime']
            assert data['gather_finished_datetime']
            assert data['gather_success']

        fetcher.run_fetch()
        assert exists(join(tmpdir, 'test','v1', 'file1.json'))

        with MetadataDB(join(tmpdir, 'test', 'v1')) as metadata_db
            data = metadata_db.get_dict()
            assert data['file_status']
            assert data['fetch_success']
            assert data['fetch_start_datetime']
            assert data['fetch_finished_datetime']

        database.create_tables(drop=True)
        fetcher.run_store()
        


class Empty(Source):
    pass

def test_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(AttributeError):
            fetcher = Empty(tmpdir)


class BadUrls(Source):
    publisher_name = 'test'
    url = 'test_url'
    source_id = 'test'
    data_version = 'v1'

    def gather_all_download_urls(self):
        yield {'url': 'https://thisaddressreallyshouldnotexists.com',
               'filename': 'file1.json',
               'data_type': 'releases',
               'errors': []}
        yield {'url': 'https://httpstat.us/500',
               'filename': 'file2.json',
               'data_type': 'releases',
               'errors': []}


def test_bad_url():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = BadUrls(tmpdir)
        fetcher.run_gather()
        fetcher.run_fetch()

        with MetadataDB(join(tmpdir, 'test', 'v1')) as metadata_db
            data = metadata_db.get_dict()
            assert not data['fetch_success']
            for value in data['file_status'].values():
                assert not value['fetch_success']
                assert value['fetch_errors']


class BadGather(Source):
    publisher_name = 'test'
    url = 'test_url'
    source_id = 'test'
    data_version = 'v1'

    def gather_all_download_urls(self):
        yield {'url': 'https://raw.githubusercontent.com/open-contracting/sample-data/5bcbfcf48bf6e6599194b8acae61e2c6e8fb5009/fictional-example/1.1/ocds-213czf-000-00001-02-tender.json',
               'filename': 'file1.json',
               'data_type': 'releases',
               'errors': ['not worked']}


def test_bad_gather():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = BadGather(tmpdir)
        fetcher.run_gather()

        with MetadataDB(join(tmpdir, 'test', 'v1')) as metadata_db
            data = metadata_db.get_dict()
            assert not data['gather_success']
            assert data['gather_finished_datetime']
            assert data['gather_failure_datetime']
            assert data['file_status']['file1.json']['gather_errors'] == ['not worked']

        with pytest.raises(Exception):
            fetcher.run_fetch()


class ExceptionGather(Source):
    publisher_name = 'test'
    url = 'test_url'
    source_id = 'test'
    data_version = 'v1'

    def gather_all_download_urls(self):
        raise IndexError


def test_exception_gather():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = ExceptionGather(tmpdir)
        fetcher.run_gather()

        with MetadataDB(join(tmpdir, 'test', 'v1')) as metadata_db
            data = metadata_db.get_dict()
            assert not data['gather_success']
            assert data['gather_failure_exception'] == 'IndexError()'
            assert data['gather_finished_datetime']
            assert data['gather_failure_datetime']

        with pytest.raises(Exception):
            fetcher.run_fetch()

def test_create_tables():
    database.create_tables(drop=True)
    database.insert_releases([
        {'source_id': 'test',
         'sample': False,
         'data_version': '2018-01-01-10-10-10',
         'file': 'moo',
         'package_data': {},
         'release': {"moo":"moo"}},
        {'source_id': 'test2',
         'sample': False,
         'data_version': '2018-01-01-10-10-10',
         'file': 'moo',
         'package_data': {},
         'release': {"moo":"moo"}},
    ])
    database.delete_releases('test')
