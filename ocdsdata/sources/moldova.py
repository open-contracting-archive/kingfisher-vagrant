from ocdsdata.base import Source
from ocdsdata.util import save_content


class MoldovaSource(Source):
    publisher_name = 'Moldova'
    url = 'http://data.dsp.im'
    source_id = 'moldova'

    def gather_all_download_urls(self):

        # You can get a list of files from http://moldova-ocds.yipl.com.np/multiple-file-api/releases.json
        # ... but the JSON is malformed and needs fixing by hand.
        # So we are just going straight for the years.

        if self.sample:
            return [{
                'url': 'http://opencontracting.date.gov.md/ocds-api/year/2017',
                'filename': 'sample.json',
                'data_type': 'release_package',
            }]

        out = []
        for year in range(2012, 2018):
            out.append({
                'url': 'http://opencontracting.date.gov.md/ocds-api/year/%d' % year,
                'filename': 'year-%d.json' % year,
                'data_type': 'release_package',
            })
        return out

    # @rate_limited(1)
    def save_url(self, filename, data, file_path):
        return [], save_content(data['url'], file_path)
