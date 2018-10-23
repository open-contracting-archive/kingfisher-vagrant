from ocdskingfisher import util
from ocdskingfisher.base import Source
import hashlib


class AfghanistanRecordsSource(Source):
    publisher_name = 'Afghanistan'
    url = 'https://ocds.ageops.net/'
    source_id = 'afghanistan_records'

    def gather_all_download_urls(self):

        r = util.get_url_request('https://ocds.ageops.net/api/ocds/records')
        if r[1]:
            raise Exception(r[1])
        r = r[0]
        out = []
        for data in r.json():
            if not self.sample or (self.sample and len(out) < 10):
                out.append({
                    'url': data,
                    'filename': hashlib.md5(data.encode('utf-8')).hexdigest(),
                    'data_type': 'record',
                })
        return out
