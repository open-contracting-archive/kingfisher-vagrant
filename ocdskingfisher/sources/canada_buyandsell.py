from ocdskingfisher.base import Source


class CanadaBuyAndSellSource(Source):
    """
    Bulk downloads: https://buyandsell.gc.ca/procurement-data/open-contracting-data-standard-pilot
    """

    publisher_name = 'Buy And Sell'
    url = 'https://buyandsell.gc.ca'
    source_id = 'canada_buyandsell'

    def gather_all_download_urls(self):
        if self.sample:
            return [
                {
                    'url': 'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-13-14.json',
                    'filename': '2013-14.json',
                    'data_type': 'release_package',
                }]

        return [
            {
                'url': 'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-13-14.json',
                'filename': '2013-14.json',
                'data_type': 'release_package',
            },
            {
                'url': 'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-14-15.json',
                'filename': '2014-15.json',
                'data_type': 'release_package',
            },
            {
                'url': 'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-15-16.json',
                'filename': '2015-16.json',
                'data_type': 'release_package',
            },
            {
                'url': 'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-16-17.json',
                'filename': '2016-17.json',
                'data_type': 'release_package',
            },
        ]
