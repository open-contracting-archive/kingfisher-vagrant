from ocdsdata.base import Source
import requests

class MexicoCDMXSource(Source):
    publisher_name = 'Mexico CDMX'
    url = 'http://www.contratosabiertos.cdmx.gob.mx'
    source_id = 'mexico_cdmx'

    def gather_all_download_urls(self):
        r = requests.get('http://www.contratosabiertos.cdmx.gob.mx/api/contratos/todos')
        datas = r.json()
        out = []
        for data in datas:
            if not self.sample or (self.sample and len(out) < 10):
                out.append({
                    'url': data['uri'],
                    'filename': 'id%s.json' % data['id'],
                    'data_type': 'release_package',
                    'errors': []
                })
        return out
