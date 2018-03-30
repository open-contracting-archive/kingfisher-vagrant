from os.path import join, exists
import tempfile
import json

import pytest

from .base import Fetcher
from . import util
from . import database

#Monkey patch to make tests run a lot faster
util.RETRY_TIME = 0.1

class Basic(Fetcher):
    publisher_name = 'test'
    url = 'test_url'
    output_directory = 'test'

    def gather_all_download_urls(self):
        yield ('https://raw.githubusercontent.com/open-contracting/sample-data/5bcbfcf48bf6e6599194b8acae61e2c6e8fb5009/fictional-example/1.1/ocds-213czf-000-00001-02-tender.json', 
               'file1.json',
               'releases',
               [])

def test_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = Basic(tmpdir)
        metadata_file = join(tmpdir, 'test', '_fetch_metadata.json')
        assert exists(metadata_file)

        with open(metadata_file) as f:
            data = json.load(f)
            assert data['publisher_name'] == 'test'
            assert data['url'] == 'test_url'
            assert data['metadata_creation_datetime']

        fetcher.run_gather()
        with open(metadata_file) as f:
            data = json.load(f)
            assert data['gather_start_datetime']
            assert data['gather_finished_datetime']
            assert data['gather_success']

        fetcher.run_fetch()
        assert exists(join(tmpdir, 'test', 'file1.json'))

        with open(metadata_file) as f:
            data = json.load(f)
            assert data['file_status']
            assert data['fetch_success']
            assert data['fetch_start_datetime']
            assert data['fetch_finished_datetime']


class Empty(Fetcher):
    pass

def test_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(AttributeError):
            fetcher = Empty(tmpdir)


class BadUrls(Fetcher):
    publisher_name = 'test'
    url = 'test_url'
    output_directory = 'test'

    def gather_all_download_urls(self):
        yield ('https://thisaddressreallyshouldnotexists.com',
               'file1.json',
               'releases',
               [])
        yield ('https://httpstat.us/500',
               'file2.json',
               'releases',
               [])


def test_bad_url():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = BadUrls(tmpdir)
        fetcher.run_gather()
        fetcher.run_fetch()
        metadata_file = join(tmpdir, 'test', '_fetch_metadata.json')

        with open(metadata_file) as f:
            data = json.load(f)
            assert not data['fetch_success']
            for value in data['file_status'].values():
                assert not value['fetch_success']
                assert value['fetch_errors']


class BadGather(Fetcher):
    publisher_name = 'test'
    url = 'test_url'
    output_directory = 'test'

    def gather_all_download_urls(self):
        yield ('https://raw.githubusercontent.com/open-contracting/sample-data/5bcbfcf48bf6e6599194b8acae61e2c6e8fb5009/fictional-example/1.1/ocds-213czf-000-00001-02-tender.json',
               'file1.json',
               'releases',
               ['not worked'])


def test_bad_gather():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = BadGather(tmpdir)
        fetcher.run_gather()
        metadata_file = join(tmpdir, 'test', '_fetch_metadata.json')

        with open(metadata_file) as f:
            data = json.load(f)
            assert not data['gather_success']
            assert data['gather_finished_datetime']
            assert data['gather_failure_datetime']
            assert data['file_status']['file1.json']['gather_errors'] == ['not worked']

        with pytest.raises(Exception):
            fetcher.run_fetch()


class ExceptionGather(Fetcher):
    publisher_name = 'test'
    url = 'test_url'
    output_directory = 'test'

    def gather_all_download_urls(self):
        raise IndexError


def test_exception_gather():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = ExceptionGather(tmpdir)
        fetcher.run_gather()
        metadata_file = join(tmpdir, 'test', '_fetch_metadata.json')

        with open(metadata_file) as f:
            data = json.load(f)
            assert not data['gather_success']
            assert data['gather_failure_exception'] == 'IndexError()'
            assert data['gather_finished_datetime']
            assert data['gather_failure_datetime']

        with pytest.raises(Exception):
            fetcher.run_fetch()

def test_create_tables():
    database.create_tables(drop=True)
    database.insert_releases([
        {'output_directory': 'test',
         'file': 'moo',
         'package_data': {},
         'release': {"moo":"moo"}},
        {'output_directory': 'test2',
         'file': 'moo',
         'package_data': {},
         'release': {"moo":"moo"}},
    ])
    database.delete_releases('test')
