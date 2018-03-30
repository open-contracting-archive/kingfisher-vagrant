from ocdsdata.base import Source

class CanadaBuyAndSellSource(Source):
    publisher_name = 'Buy And Sell'
    url = 'https://buyandsell.gc.ca'
    source_id = 'canada_buyandsell'

    def gather_all_download_urls(self):
        return [
            [
                'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-13-14.json',
                '2013-14.json',
                'release_package',
                []
            ],
            [
                'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-14-15.json',
                '2014-15.json',
                'release_package',
                []
            ],
            [
                'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-15-16.json',
                '2015-16.json',
                'release_package',
                []
            ],
            [
                'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-16-17.json',
                '2016-17.json',
                'release_package',
                []
            ],
        ]

