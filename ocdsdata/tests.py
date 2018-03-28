from os.path import join, exists
import tempfile
import json

from .base import Fetcher

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
            assert data['download_status']
            assert data['fetch_success']
            assert data['fetch_start_datetime']
            assert data['fetch_finished_datetime']

