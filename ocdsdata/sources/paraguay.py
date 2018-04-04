from ocdsdata.base import Source
import requests
import csv
import json
from ocdsdata.util import save_content
import hashlib

REQUEST_TOKEN = "Basic " \
                "ODhjYmYwOGEtMDcyMC00OGY1LWFhYWUtMWVkNzVkZmFiYzZiOjNjNjQxZGQ5LWNjN2UtNDI5ZC05NWRiLWI5ODNiNmYyMDY3NA== "

class ParaguaySource(Source):
    publisher_name = 'Paraguay'
    url = 'http://data.dsp.im'
    source_id = 'paraguay'

    def gather_all_download_urls(self):
        record_package_ids = []

        for year in range(2010, (2011 if self.sample else 2019)):
            record_package_ids += self.fetchRecordPackageIDs(year)

        if self.sample:
            record_package_ids = record_package_ids[:5]

        out = []

        for record_package_id in record_package_ids:
            out.append({
                'url': 'https://www.contrataciones.gov.py:443/datos/api/v2/doc/ocds/record-package/%s' % record_package_id,
                'filename': 'record-%s.json' % record_package_id,
                'data_type': 'record_package',
                'errors': []
            })

        return out

    # @rate_limited(0.3)
    def fetchRecordPackageIDs(self, year):
        '''
        Download the CSV file for a particular year, and
        extract the list of record package IDs.
        '''
        url = 'https://www.contrataciones.gov.py/'
        url += 'images/opendata/planificaciones/%s.csv' % year
        r = requests.get(url)
        decoded_content = r.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        id_list = []
        for row in cr:
            id_list.append(row[2])
        return id_list[1:]

    # @rate_limited(0.3)
    def save_url(self, data, file_path):
        if data['data_type'] == 'record_package':

            errors = save_content(data['url'], file_path, headers={"Authorization": self.getAccessToken()})
            if errors:
                return [], errors

            additional = []

            with open(file_path) as f:
                json_data = json.load(f)

            if 'packages' in json_data:
                for url in json_data['packages']:

                    url = url \
                        .replace('/datos/id/', '/datos/api/v2/doc/ocds/') \
                        .replace('.json', '')

                    additional.append({
                        'url': url,
                        'filename': 'packages-%s.json' % hashlib.md5(url.encode('utf-8')).hexdigest(),
                        'data_type': 'release_package',
                        'errors': []
                    })

            return additional, []
        else:
            return [], save_content(data['url'], file_path, headers={"Authorization": self.getAccessToken()})

    access_token = None

    def getAccessToken(self):
        if self.access_token:
            return "Bearer " + self.access_token
        else:
            correct = False
            json = ''
            while not correct:
                r = requests.post("https://www.contrataciones.gov.py:443/datos/api/oauth/token",
                                  headers={"Authorization": REQUEST_TOKEN})
                try:
                    json = r.json()['access_token']
                    correct = True
                except:
                    correct = False
            self.access_token = json
            return "Bearer " + json
