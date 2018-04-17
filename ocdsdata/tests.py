from os.path import join, exists
import tempfile

import pytest

from .base import Source
from . import util
from . import database
from ocdsdata.metadata_db import MetadataDB
import json

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
               'data_type': 'release_package',
               'errors': []}

def test_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = Basic(tmpdir)
        metadata_file = join(tmpdir, 'test', 'v1', 'metadb.sqlite3')
        assert exists(metadata_file)

        metadata_db = MetadataDB(join(tmpdir, 'test', 'v1'))
        data = metadata_db.get_dict()
        assert data['publisher_name'] == 'test'
        assert data['base_url'] == 'test_url'
        assert data['session_start_datetime']
        del data, metadata_db

        fetcher.run_gather()
        metadata_db = MetadataDB(join(tmpdir, 'test', 'v1'))
        data = metadata_db.get_dict()
        assert data['gather_start_datetime']
        assert data['gather_finished_datetime']
        assert data['gather_success']
        del data, metadata_db


        fetcher.run_fetch()
        assert exists(join(tmpdir, 'test','v1', 'file1.json'))

        metadata_db = MetadataDB(join(tmpdir, 'test', 'v1'))
        data = metadata_db.get_dict()
        assert data['file_status']
        assert data['fetch_success']
        assert data['fetch_start_datetime']
        assert data['fetch_finished_datetime']
        del data, metadata_db


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

        metadata_db = MetadataDB(join(tmpdir, 'test', 'v1'))
        data = metadata_db.get_dict()
        assert not data['fetch_success']
        for value in data['file_status'].values():
            assert not value['fetch_success']
            assert value['fetch_errors']


class BadFetchErrors(Source):
    publisher_name = 'test'
    url = 'test_url'
    source_id = 'test'
    data_version = 'v1'

    def gather_all_download_urls(self):
        yield {'url': 'https://raw.githubusercontent.com/open-contracting/sample-data/5bcbfcf48bf6e6599194b8acae61e2c6e8fb5009/fictional-example/1.1/ocds-213czf-000-00001-02-tender.json',
               'filename': 'file1.json',
               'data_type': 'releases',
               'errors': []}

    def save_url(self, file_name, data, file_path):
        return [], ['A really bad error occured!']


def test_bad_fetch_errors():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = BadFetchErrors(tmpdir)
        fetcher.run_gather()
        fetcher.run_fetch()

        metadata_db = MetadataDB(join(tmpdir, 'test', 'v1'))
        data = metadata_db.get_dict()
        assert data['gather_success']
        assert data['gather_finished_datetime']
        assert not data['fetch_success']
        assert not data['file_status']['file1.json']['fetch_success']
        assert data['file_status']['file1.json']['fetch_start_datetime']
        assert data['file_status']['file1.json']['fetch_finished_datetime']
        assert data['file_status']['file1.json']['fetch_errors'] == ['A really bad error occured!']

        with pytest.raises(Exception):
            fetcher.run_store()

class BadFetchException(Source):
    publisher_name = 'test'
    url = 'test_url'
    source_id = 'test'
    data_version = 'v1'

    def gather_all_download_urls(self):
        yield {'url': 'https://raw.githubusercontent.com/open-contracting/sample-data/5bcbfcf48bf6e6599194b8acae61e2c6e8fb5009/fictional-example/1.1/ocds-213czf-000-00001-02-tender.json',
               'filename': 'file1.json',
               'data_type': 'releases',
               'errors': []}

    def save_url(self, file_name, data, file_path):
        raise Exception('Whoops')


def test_bad_fetch_exception():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = BadFetchException(tmpdir)
        fetcher.run_gather()
        fetcher.run_fetch()

        metadata_db = MetadataDB(join(tmpdir, 'test', 'v1'))
        data = metadata_db.get_dict()
        assert data['gather_success']
        assert data['gather_finished_datetime']
        assert not data['fetch_success']
        assert not data['file_status']['file1.json']['fetch_success']
        assert data['file_status']['file1.json']['fetch_start_datetime']
        assert data['file_status']['file1.json']['fetch_finished_datetime']
        assert data['file_status']['file1.json']['fetch_errors'] == ["Exception('Whoops',)"]

        with pytest.raises(Exception):
            fetcher.run_store()


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

        metadata_db = MetadataDB(join(tmpdir, 'test', 'v1'))
        data = metadata_db.get_dict()
        assert not data['gather_success']
        assert data['gather_errors'] == 'IndexError()'
        assert data['gather_finished_datetime']
        assert data['gather_errors']

        with pytest.raises(Exception):
            fetcher.run_fetch()

def test_create_tables():
    database.create_tables(drop=True)

def test_database_get_hash_md5_for_data():
    assert database.get_hash_md5_for_data({'cats': 'many'}) == '538dd075f4a37d77be84c683b711d644'


def test_database_get_hash_md5_for_data2():
    assert database.get_hash_md5_for_data({'cats': 'none'}) == '562c5f4221c75c8f08da103cc10c4e4c'




