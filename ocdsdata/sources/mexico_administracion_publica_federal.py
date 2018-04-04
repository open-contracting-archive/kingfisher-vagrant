from ocdsdata.base import Source
import requests


class MexicoAdministracionPublicaFederal(Source):
    publisher_name = 'Mexico Administracion Publica Fedaral'
    url = 'https://api.datos.gob.mx/v1/contratacionesabiertas'
    source_id = 'mexico_administracion_publica_federal'

    def gather_all_download_urls(self):
        url = 'https://api.datos.gob.mx/v1/contratacionesabiertas?page=%d'
        if self.sample:
            return [{
                'url': url % 1,
                'filename': 'sample.json',
                'data_type': 'release_package',
                'errors': []
            }]

        r = requests.get(url % 2)
        data = r.json()
        total = data['pagination']['total']
        page = 1
        out = []
        limit = data['pagination']['pageSize']
        while ((page-1)*limit) < total:
            out.append({
                'url': url % page,
                'filename': 'page%d.json' % page,
                'data_type': 'release_package',
                'errors': []
            })
            page += 1
        return out
