from ocdskingfisher import util
from ocdskingfisher.base import Source
from ocdskingfisher.util import save_content
import json


class AfghanistanReleasesSource(Source):
    publisher_name = 'Afghanistan'
    url = 'https://ocds.ageops.net/'
    source_id = 'afghanistan_releases'

    def gather_all_download_urls(self):

        if self.sample:
            return [{
                'url': 'https://ocds.ageops.net/api/ocds/releases/2018-09-23',
                'filename': '2018-09-23.json',
                'data_type': 'meta',
                'priority': 10
            }]

        r = util.get_url_request('https://ocds.ageops.net/api/ocds/releases/dates')
        if r[1]:
            raise Exception(r[1])
        r = r[0]
        out = []
        for data in r.json():
            out.append({
                'url': data,
                'filename': data[-10:] + '.json',
                'data_type': 'meta',
                'priority': 10
            })
        return out

    def save_url(self, filename, data, file_path):

        save_content_response = save_content(data['url'], file_path)
        if save_content_response.errors:
            return self.SaveUrlResult(errors=save_content_response.errors, warnings=save_content_response.warnings)

        additional = []

        if data['data_type'] == 'meta':

            with open(file_path) as f:
                json_data = json.load(f)

            for item in json_data:
                if not self.sample or (self.sample and len(additional) < 10):
                    additional.append({
                        'url': item,
                        'filename': 'release-%s.json' % item.split('/')[-1],
                        'data_type': 'release',
                    })

        return self.SaveUrlResult(additional_files=additional, warnings=save_content_response.warnings)
