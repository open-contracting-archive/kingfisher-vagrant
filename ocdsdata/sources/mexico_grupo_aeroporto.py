from ocdsdata.base import Source
import requests
from ocdsdata.util import save_content
import json
import hashlib

class MexicoGrupoAeroportoSource(Source):
    publisher_name = 'Mexico Grupo Aeroporto'
    url = 'https://datos.gob.mx/busca/organization/gacm'
    source_id = 'mexico_grupo_aeroporto'

    def gather_all_download_urls(self):
        r = requests.get('https://datos.gob.mx/busca/api/3/action/package_search?q=organization:gacm&rows=500')
        data = r.json()
        urls = []
        for result in data['result']['results']:
            for resource in result['resources']:
                if not self.sample or (self.sample and len(urls) < 10):
                    if resource['format'] == 'JSON':
                        urls.append({
                            'url': resource['url'],
                            'filename': resource['url'].split('/')[-1],
                            'data_type': 'release_package',
                            'errors': []
                        })
        return urls
