from io import BytesIO
from zipfile import ZipFile

import requests

from ocdsdata.base import Source
from ocdsdata.util import save_content

REQUEST_TOKEN = '06034873-f3e1-47b8-8bfb-45b11b3fc83d'
CLIENT_SECRET = 'e606642e20667a6b7b46b9644ce40a85d11a84da173d4d26f65cd5826121ec01'


class ParaguayHaciendaSource(Source):
    publisher_name = 'Paraguay Hacienda'
    url = 'http://data.dsp.im'
    source_id = 'paraguay_hacienda'

    def gather_all_download_urls(self):
        release_package_ids = []

        for year in range(2011, (2012 if self.sample else 2018)):
            release_package_ids += self.get_tender_ids(year)

        release_package_ids = set(release_package_ids)
        release_package_ids = list(release_package_ids)

        if self.sample:
            release_package_ids = release_package_ids[:5]

        out = []
        print('Fetching %d releases' % len(release_package_ids))
        for release_package_id in release_package_ids:
            out.append({
                'url': 'https://datos.hacienda.gov.py:443/odmh-api-v1/rest/api/v1/ocds/release-package/%s' %
                       release_package_id,
                'filename': 'release-%s.json' % release_package_id,
                'data_type': 'release_package',
            })

        return out

    @staticmethod
    def get_tender_ids(year):
        url = 'https://datos.hacienda.gov.py/odmh-core/rest/cdp/datos/cdp_%s.zip' % year
        print('Getting url %s' % url)
        resp = requests.get(url).content
        zipfile = ZipFile(BytesIO(resp))
        ids = []
        for line in zipfile.open('cdp_%s.csv' % year).readlines():
            line = str(line).split(',')
            id = line[-4].replace('"', '').split('/')[-1]
            if id is not '':
                ids.append(id)
        return ids

    def save_url(self, filename, data, file_path):
        if data['data_type'] == 'release_package':
            print('Saving %s ' % data['url'])
            errors = save_content(data['url'], file_path, headers={"Authorization": self.get_access_token()})
            if errors:
                return [], errors
        else:
            return [], save_content(data['url'], file_path, headers={"Authorization": self.get_access_token()})

    access_token = None

    @staticmethod
    def get_access_token():
        correct = False
        token = ''
        while not correct:
            r = requests.post("https://datos.hacienda.gov.py:443/odmh-api-v1/rest/api/v1/auth/token",
                              headers={"Authorization": REQUEST_TOKEN}, json={"clientSecret": "%s" % CLIENT_SECRET})
            try:
                token = r.json()['accessToken']
                correct = True
            except Exception as e:
                print(e)
                correct = False
        return token
