from ocdsdata.base import Fetcher
import requests


class CanadaMontreal(Fetcher):
    publisher_name = 'Montreal'
    url = 'https://ville.montreal.qc.ca'

    def __init__(self, base_dir, remove_dir=False, output_directory=None):
        super().__init__(base_dir, remove_dir=remove_dir, output_directory=output_directory)

    def gather_all_download_urls(self):
        url = 'https://ville.montreal.qc.ca/vuesurlescontrats/api/releases.json?limit=1'
        r = requests.get(url)
        data = r.json()
        total = data['meta']['count']
        offset = 0
        out = []
        limit = 10000
        while offset < total:
            out.append([
                'https://ville.montreal.qc.ca/vuesurlescontrats/api/releases.json?limit=%d&offset=%d' % (limit, offset),
                'offset%d.json' % offset,
                'release_package',
                []
            ])
            offset += limit
        return out
