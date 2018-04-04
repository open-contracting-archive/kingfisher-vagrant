from ocdsdata.base import Source
import requests
from ocdsdata.util import save_content
import json
import hashlib

class MexicoJaliscoSource(Source):
    publisher_name = 'Mexico Jalisco'
    url = 'http://www.contratosabiertos.cdmx.gob.mx'
    source_id = 'mexico_jalisco'

    def gather_all_download_urls(self):
        r = requests.get('https://contratacionesabiertas.jalisco.gob.mx/OCApi/2017/contracts')
        datas = r.json()
        out = []
        for data in datas:
            if not self.sample or (self.sample and len(out) < 10):
                out.append({
                    'url': data['URIContract'],
                    'filename': 'id%s.json' % data['ocid'],
                    'data_type': 'record_package',
                    'errors': []
                })
        return out

    def save_url(self, filename, data, file_path):
        if data['data_type'] == 'record_package':

            errors = save_content(data['url'], file_path)
            if errors:
                return [], errors

            additional = []

            with open(file_path) as f:
                json_data = json.load(f)

            if 'packages' in json_data:
                for url in json_data['packages']:
                    additional.append({
                        'url': url,
                        'filename': 'packages-%s.json' % hashlib.md5(url.encode('utf-8')).hexdigest(),
                        'data_type': 'release_package',
                        'errors': []
                    })

            return additional, []
        else:
            return [], save_content(data['url'], file_path)
