from ocdskingfisher.base import Source
import datetime


class ScotlandSource(Source):
    """
    API documentation and bulk downloads: https://www.publiccontractsscotland.gov.uk/NoticeDownload/Download.aspx
    """

    publisher_name = 'Scotland'
    url = 'https://www.publiccontractsscotland.gov.uk/NoticeDownload/Download.aspx'
    source_id = 'scotland'

    def gather_all_download_urls(self):
        if self.sample:
            return [
                {
                    'url': 'https://api.publiccontractsscotland.gov.uk/v1/Notices?dateFrom=2016-10-01&outputType=1',
                    'filename': 'sample.json',
                    'data_type': 'release_package',
                }
            ]

        now = datetime.datetime.today()
        # It's meant to go back a year, but in testing it seemed to be year minus one day!
        marker = now - datetime.timedelta(days=364)
        out = []
        while marker <= now:
            datestring = '{:04d}-{:02d}-{:02d}'.format(marker.year, marker.month, marker.day)
            out.append({
                'url': 'https://api.publiccontractsscotland.gov.uk/v1/Notices?dateFrom={}&outputType=1'.format(datestring),
                'filename': '{}.json'.format(datestring),
                'data_type': 'release_package',
            })
            marker = marker + datetime.timedelta(days=14)
        return out
