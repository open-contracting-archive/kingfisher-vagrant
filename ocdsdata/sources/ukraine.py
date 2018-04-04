from ocdsdata.base import Source
import requests
import lxml.html
from ocdsdata.util import save_content
import hashlib

class UkraineSource(Source):
    publisher_name = 'Ukraine'
    url = 'http://ocds.prozorro.openprocurement.io/'
    source_id = 'ukraine'

    def gather_all_download_urls(self):
        r = requests.get('http://ocds.prozorro.openprocurement.io/')
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

            r = requests.get(data['url'])
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





