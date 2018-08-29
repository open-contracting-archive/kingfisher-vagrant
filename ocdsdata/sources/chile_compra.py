from ocdsdata.base import Source
from ocdsdata import util
import json


class ChileCompraSource(Source):
    publisher_name = 'ChileCompra'
    url = 'https://desarrolladores.mercadopublico.cl/docs/services/5a9ed02f718ed712f4403e75/operations/listado-a-o-mes?'
    source_id = 'chile_compra'

    def gather_all_download_urls(self):

        if self.sample:
            return [{
                'url': 'https://apis.mercadopublico.cl/OCDS/data/listaA%C3%B1oMes/2017/10',
                'filename': 'sample.json',
                'data_type': 'meta',
                'priority': 10,
            }]

        out = []
        for year in range(2008, 2019):
            for month in range(1, 13):
                out.append({
                    'url': 'https://apis.mercadopublico.cl/OCDS/data/listaA%C3%B1oMes/{}/{:02d}'.format(year, month),
                    'filename': 'year-{}-month-{:02d}.json'.format(year, month),
                    'data_type': 'meta',
                    'priority': 10,
                })
        return out

    def save_url(self, filename, data, file_path):
        if data['data_type'] == 'meta':

            response, errors = util.get_url_request(data['url'])
            if errors:
                return self.SaveUrlResult(errors=errors)

            data = json.loads(response.text)

            additional = []

            if "ListadoOCDS" in data.keys():
                for data_item in data["ListadoOCDS"]:
                    if not self.sample or (self.sample and len(additional) < 10):
                        additional.append({
                                        'url': data_item['URLTender'],
                                        'filename': 'data-%s.json' % data_item['Codigo'],
                                        'data_type': 'release_package',
                                        'priority': 1,
                                    })

            return self.SaveUrlResult(additional_files=additional)

        else:
            return super(ChileCompraSource, self).save_url(file_name=filename, data=data, file_path=file_path)
