import json

from ocdskingfisher.base import Source
from ocdskingfisher.util import save_content


class ArmeniaSource(Source):
    publisher_name = 'Armenia'
    url = 'https://armeps.am/ocds/release'
    source_id = 'armenia'

    def gather_all_download_urls(self):
        url = 'https://armeps.am/ocds/release'
        out = [{
            'url': url,
            'filename': 'page-1-.json',
            'data_type': 'release_package',
        }]
        return out

    def save_url(self, filename, data, file_path):
        if data['data_type'] == 'release_package':

            save_content_response = save_content(data['url'], file_path)
            if save_content_response.errors:
                return self.SaveUrlResult(errors=save_content_response.errors, warnings=save_content_response.warnings)

            additional = []

            with open(file_path) as f:
                json_data = json.load(f)

            page = int(filename.split('-')[1])
            if 'next_page' in json_data and 'uri' in json_data['next_page'] and (not self.sample or page < 3):
                page += 1
                additional.append({
                    'url': json_data['next_page']['uri'],
                    'filename': 'page-%d-.json' % page,
                    'data_type': 'release_package',
                })
            return self.SaveUrlResult(additional_files=additional, warnings=save_content_response.warnings)
