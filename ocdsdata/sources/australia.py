import hashlib
import json

from ocdsdata.base import Source
from ocdsdata.util import save_content


class AustraliaSource(Source):
    publisher_name = 'Australia'
    url = 'https://tenders.nsw.gov.au'
    source_id = 'australia'

    def gather_all_download_urls(self):
        release_types = ['planning', 'tender', 'contract']
        url = 'https://tenders.nsw.gov.au'
        url += '/?event=public.api.%s.search&ResultsPerPage=50'
        out = []
        for r in release_types:
            out.append({
                'url': url % r,
                'filename': 'type-%s-page-1-.json' % r,
                'data_type': 'release_package',
                'errors': []
            })

        return out

    def save_url(self, filename, data, file_path):
        link = 'links'
        if data['data_type'] == 'release_package':

            errors = save_content(data['url'], file_path)
            if errors:
                return [], errors

            additional = []

            if filename.startswith('type'):

                with open(file_path) as f:
                    json_data = json.load(f)

                page = int(filename.split('-')[3])
                type = filename.split('-')[1]
                if link in json_data and 'next' in json_data[link] and (not self.sample or page < 3):
                    page += 1
                    additional.append({
                        'url': json_data[link]['next'],
                        'filename': 'type-%s-page-%d-.json' % (type, page),
                        'data_type': 'release_package',
                        'errors': []
                    })

                count = 0
                for release in json_data['releases']:
                    if not self.sample or count < 3:
                        stage_urls = []
                        if type == 'planning':
                            uuid = release['tender']['plannedProcurementUUID']
                            stage_urls.append('https://tenders.nsw.gov.au/?event=public.api.planning.view'
                                              '&PlannedProcurementUUID=%s' % uuid)
                        if type == 'tender':
                            uuid = release['tender']['RFTUUID']
                            stage_urls.append('https://tenders.nsw.gov.au/?event=public.api.tender.view&RFTUUID=%s' % uuid)
                        if type == 'contract':
                            for award in release['awards']:
                                uuid = award['CNUUID']
                                stage_urls.append('https://tenders.nsw.gov.au/?event=public.api.contract.view&CNUUID=%s'
                                                  % uuid)
                        count += 1
                        for url in stage_urls:
                            additional.append({
                                'url': url,
                                'filename': 'packages-%s.json' % hashlib.md5(url.encode('utf-8')).hexdigest(),
                                'data_type': 'release_package',
                                'errors': []
                            })

            return additional, []