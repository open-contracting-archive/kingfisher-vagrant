from ocdskingfisher import util
from ocdskingfisher.base import Source


class CanadaMontrealSource(Source):
    publisher_name = 'Montreal'
    url = 'https://ville.montreal.qc.ca'
    source_id = 'canada_montreal'

    def gather_all_download_urls(self):

        if self.sample:
            return [{
                'url': 'https://ville.montreal.qc.ca/vuesurlescontrats/api/releases.json?limit=1000&offset=0',
                'filename': 'offset0.json',
                'data_type': 'release_package',
            }]

        url = 'https://ville.montreal.qc.ca/vuesurlescontrats/api/releases.json?limit=1'
        r = util.get_url_request(url)
        if r[1]:
            raise Exception(r[1])
        r = r[0]
        data = r.json()
        total = data['meta']['count']
        offset = 0
        out = []
        limit = 10000
        while offset < total:
            out.append({
                'url': 'https://ville.montreal.qc.ca/vuesurlescontrats/api/releases.json?limit=%d&offset=%d' % (limit, offset),
                'filename': 'offset%d.json' % offset,
                'data_type': 'release_package',
            })
            offset += limit
        return out
