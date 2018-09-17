import hashlib
import json

from ocdskingfisher.base import Source
from ocdskingfisher.util import save_content


class AustraliaNSWSource(Source):
    """
    API documentation: https://github.com/NSW-eTendering/NSW-eTendering-API
    """

    publisher_name = 'Australia NSW'
    url = 'https://tenders.nsw.gov.au'
    source_id = 'australia_nsw'

    def gather_all_download_urls(self):
        release_types = ['planning', 'tender', 'contract']
        url = 'https://tenders.nsw.gov.au'
        url += '/?event=public.api.%s.search&ResultsPerPage=1000'
        out = []
        for r in release_types:
            out.append({
                'url': url % r,
                'filename': 'type-%s-page-1-.json' % r,
                'data_type': 'meta',
                'priority': 10,
            })

        return out

    # @rate_limited(1)
    def save_url(self, filename, data, file_path):

        save_content_response = save_content(data['url'], file_path)
        if save_content_response.errors:
            return self.SaveUrlResult(errors=save_content_response.errors, warnings=save_content_response.warnings)

        additional = []

        if data['data_type'] == 'meta':

            with open(file_path) as f:
                json_data = json.load(f)

            page = int(filename.split('-')[3])
            type = filename.split('-')[1]
            if 'links' in json_data and 'next' in json_data['links'] and (not self.sample or page < 3):
                page += 1
                additional.append({
                    'url': json_data['links']['next'],
                    'filename': 'type-%s-page-%d-.json' % (type, page),
                    'data_type': 'meta',
                    'priority': 10,
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
                            'priority': 1,
                        })

        return self.SaveUrlResult(additional_files=additional, warnings=save_content_response.warnings)

    def before_check_data(self, data, override_schema_version=None):
        if not override_schema_version and isinstance(data['version'], float) and data['version'] == 1.0:
            data['version'] = '1.0'
        return data
