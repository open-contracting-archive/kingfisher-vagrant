from ocdsdata.base import Fetcher
import tempfile

class CanadaBuyAndSellFetcher(Fetcher):

    def __init__(self):

        output_directory = tempfile.mkdtemp('','canadabuyandsell')
        super().__init__('/', False, None, None, output_directory)


    def gather_all_download_urls(self):
        return [
            [
                'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-13-14.json',
                '2013-14.json',
                'json',
                []
            ],
            [
                'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-14-15.json',
                '2014-15.json',
                'json',
                []
            ],
            [
                'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-15-16.json',
                '2015-16.json',
                'json',
                []
            ],
            [
                'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-16-17.json',
                '2016-17.json',
                'json',
                []
            ],
        ]

