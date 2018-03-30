from ocdsdata.base import Fetcher
import requests
import lxml.html
from ocdsdata.util import save_content
import shutil


class MexicoAdministracionPublicaFederalFetcher(Fetcher):
    publisher_name = 'Mexico - Administracion Publica Federal'
    url = 'http://datos.gob.mx'
    source_id = 'mexico_administracion_publica_federal'


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


    def save_url(self, url, file_path):

        if url[:25] == 'https://drive.google.com/':

            r = requests.get(url)
            doc = lxml.html.fromstring(r.text)
            link = doc.get_element_by_id('uc-download-link')
            actual_url = 'https://drive.google.com' + link.get('href')

            actual_r = requests.get(actual_url)
            with open(file_path, 'wb') as f:
                f.write(actual_r.content)

            return []
        else:
            return save_content(url, file_path)
