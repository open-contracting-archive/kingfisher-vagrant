from ocdsdata.base import Fetcher
import requests
import http.client


class MexicoAdministracionPublicaFederalFetcher(Fetcher):
    publisher_name = 'Mexico - Administracion Publica Federal'
    url = 'http://datos.gob.mx'

    def __init__(self, base_dir, remove_dir=False, output_directory=None):
        super().__init__(base_dir, remove_dir=remove_dir, output_directory=output_directory)

    def gather_all_download_urls(self):
        url = 'https://datos.gob.mx/busca/api/3/action/package_search?q=organization:contrataciones-abiertas&rows=500'
        r = requests.get(url)
        data = r.json()
        out = []
        count = 0
        for details1 in data['result']['results']:
            for details2 in details1['resources']:
                if details2['format'] == 'JSON':
                    count = count + 1
                    out.append([
                        details2['url'],
                        'file%d.json' % count,
                        'release_package',
                        []
                    ])
        return out


