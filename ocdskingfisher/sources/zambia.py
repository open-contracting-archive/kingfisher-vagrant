import datetime
from zipfile import ZipFile
from io import BytesIO
from ocdskingfisher.base import Source
from ocdskingfisher import util


class ZambiaSource(Source):
    publisher_name = 'Zambia'
    url = 'https://www.zppa.org.zm/record-packages'
    source_id = 'zambia'

    def gather_all_download_urls(self):

        if self.sample:
            return [{
                'url': 'https://www.zppa.org.zm/ocds/services/recordpackage/getrecordpackage/2017/12',
                'filename': 'sample.json',
                'data_type': 'record_package'
            }]

        year = 2016
        month = 6
        now = datetime.datetime.now()
        out = []
        while year != now.year or month != now.month:

            # We specially move up before getting data.
            # The current year/month seems to be a valid dowload, and this way we get it.
            month += 1
            if month > 12:
                month = 1
                year += 1

            # One month is missing. I have no idea why.
            if year == 2017 and month == 4:
                continue

            # now list the data
            out.append({
                'url': 'https://www.zppa.org.zm/ocds/services/recordpackage/getrecordpackage/{}/{}'.format(year, month),
                'filename': 'year{}month{}.json'.format(year, month),
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
