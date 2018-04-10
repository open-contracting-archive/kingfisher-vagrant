import hashlib

import lxml.html

from ocdsdata import util
from ocdsdata.base import Source
from ocdsdata.util import save_content


class UkraineSource(Source):
    publisher_name = 'Ukraine'
    url = 'http://ocds.prozorro.openprocurement.io/'
    source_id = 'ukraine'

    def gather_all_download_urls(self):
        r = util.get_url_request('http://ocds.prozorro.openprocurement.io/')
        if r[1]:
            raise Exception(r[1])
        r = r[0]
        doc = lxml.html.fromstring(r.text)
        out = []
        for item in doc.xpath('//li'):
            url = item.xpath('a')[0].get('href')
            if not self.sample or (self.sample and len(out) < 1):
                out.append({
                    'url': 'http://ocds.prozorro.openprocurement.io/%s' % url,
                    'filename': 'meta-%s.json' % url,
                    'data_type': 'meta',
                    'errors': []
                })

        return out

    def save_url(self, filename, data, file_path):
        if data['data_type'] == 'meta':

            r = util.get_url_request(data['url'])
            if r[1]:
                raise Exception(r[1])
            r = r[0]
            doc = lxml.html.fromstring(r.text)

            additional = []

            for item in doc.xpath('//li'):
                url_bit = item.xpath('a')[0].get('href')
                if url_bit != 'index.html':
                    url = '%s/%s' % ( data['url'], url_bit )
                    if not self.sample or (self.sample and len(additional) < 3):
                        additional.append({
                            'url': url,
                            'filename': 'packages-%s.json' % hashlib.md5(url.encode('utf-8')).hexdigest(),
                            'data_type': 'release_package',
                            'errors': []
                        })

            return additional, []
        else:
            return [], save_content(data['url'], file_path)





