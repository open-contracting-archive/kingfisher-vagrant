from ocdsdata import util
from ocdsdata.base import Source


class MexicoGrupoAeroportoSource(Source):
    publisher_name = 'Mexico Grupo Aeroporto'
    url = 'https://datos.gob.mx/busca/organization/gacm'
    source_id = 'mexico_grupo_aeroporto'

    def gather_all_download_urls(self):
        r = util.get_url_request('https://datos.gob.mx/busca/api/3/action/package_search?q=organization:gacm&rows=500')
        if r[1]:
            raise Exception(r[1])
        r = r[0]
        data = r.json()
        urls = []
        for result in data['result']['results']:
            for resource in result['resources']:
                if not self.sample or (self.sample and len(urls) < 10):
                    if resource['format'] == 'JSON':
                        urls.append({
                            'url': resource['url'],
                            'filename': resource['url'].split('/')[-1],
                            'data_type': 'release_package_list' if resource['name'] == "CONCENTRADO ARCHIVO JSON" else 'release_package',
                        })
        return urls
