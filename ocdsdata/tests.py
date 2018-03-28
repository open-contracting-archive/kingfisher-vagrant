from os.path import join, exists
import tempfile
import json

from .base import Fetcher

class Basic(Fetcher):
    publisher_name = 'test'
    url = 'test'
    output_directory = 'test'

    def gather_all_download_urls(self):
        yield ('https://raw.githubusercontent.com/open-contracting/sample-data/5bcbfcf48bf6e6599194b8acae61e2c6e8fb5009/fictional-example/1.1/ocds-213czf-000-00001-02-tender.json', 
               'file1.json',
               'releases',
               [])

def test_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        Basic(tmpdir).run_gather()
        metadata_file = join(tmpdir, 'test', '_fetch_metadata.json')
        assert exists(metadata_file)

        with open(metadata_file) as f:
            data = json.load(f)
            assert data['gather_success']

        Basic(tmpdir).run_fetch()
        assert exists(join(tmpdir, 'test', 'file1.json'))

        with open(metadata_file) as f:
            data = json.load(f)
            assert data['fetch_success']

