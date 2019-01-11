import hashlib
from zipfile import ZipFile
from io import BytesIO

import requests

from ocdskingfisher.base import Source
from ocdskingfisher import util


class ZambiaSource(Source):
    publisher_name = 'Zambia'
    url = 'https://www.zppa.org.zm/record-packages'
    source_id = 'zambia'

    def gather_all_download_urls(self):

        base_url = 'https://www.zppa.org.zm/ocds/services/recordpackage/getrecordpackagelist'
        if self.sample:
            return [{
                'url': requests.get(base_url).json()
                ['packagesPerMonth'][0],
                'filename': 'sample.json',
                'data_type': 'record_package'
            }]

        out = []
        for url in requests.get(base_url).json()['packagesPerMonth']:
            out.append({
                'url': url,
                'filename': 'record-package-%s.json' % hashlib.md5(url.encode('utf-8')).hexdigest(),
                'data_type': 'record_package'
            })
        return out

    def save_url(self, filename, data, file_path):

        response, errors = util.get_url_request(data['url'])
        if errors:
            return self.SaveUrlResult(errors=errors)

        zipfile = ZipFile(BytesIO(response.content))
        read_file_name = zipfile.namelist()[0]

        try:
            with open(file_path, 'wb') as f:
                f.write(zipfile.read(read_file_name))
        except Exception as e:
            return self.SaveUrlResult(errors=[str(e)])

        return self.SaveUrlResult()
