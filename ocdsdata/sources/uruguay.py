import json

from ocdsdata.base import Source
from ocdsdata import util
from ocdsdata.util import save_content


class UruguaySource(Source):
    publisher_name = 'Uruguay'
    url = 'http://www.comprasestatales.gub.uy'
    source_id = 'uruguay'

    def gather_all_download_urls(self):
        url_base = 'https://catalogodatos.gub.uy'
        url = url_base + '/api/3/action/datastore_search?resource_id=9fc590fd-0d33-4478-9193-9c44906ca388'
        out = []
        data, error = util.get_url_request(url)

        data = data.json()['result']
        while len(data['records']) > 0:
            for record in data['records']:
                if self.sample and len(out) >= 10:
                    break
                out.append({
                    'url': record['open_contracting_link'],
                    'filename': '%s.json' % record['id_compra'],
                    'data_type': 'record_package',
                })
            if self.sample:
                break
            url = url_base + data['_links']['next']
            data, error = util.get_url_request(url)
            data = data.json()['result']

        return out

    def save_url(self, filename, data, file_path):
        save_content_response = save_content(data['url'], file_path)
        if save_content_response.errors:
            return self.SaveUrlResult(errors=save_content_response.errors, warnings=save_content_response.warnings)
        additional = []
        if data['data_type'] == 'record_package':
            with open(file_path, 'r') as f:
                json_data = json.load(f)
                for release in json_data['records'][0]['releases']:
                    additional.append({
                        'url': release['url'],
                        'filename': 'release-%s.json' % release['url'].split('/')[-1],
                        'data_type': 'release_package',
                    })

        return self.SaveUrlResult(additional_files=additional)
