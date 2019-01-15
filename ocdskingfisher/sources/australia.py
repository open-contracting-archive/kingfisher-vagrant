from ocdskingfisher.base import Source


class AustraliaSource(Source):
    """
    """

    publisher_name = 'Australia'
    url = 'https://api.tenders.gov.au'
    source_id = 'australia'

    def gather_all_download_urls(self):

        if self.sample:
            return[{
                'url': "https://api.tenders.gov.au/ocds/findByDates/contractPublished/2018-01-01T00:00:00Z/2018-12-31T23:59:59Z",
                'filename': 'year-2018.json',
                'data_type': 'release_package',
            }]

        else:
            out = []
            for year in range(2004, 2020):
                url = "https://api.tenders.gov.au/ocds/findByDates/contractPublished/{}-01-01T00:00:00Z/{}-12-31T23:59:59Z".format(year, year)  # noqa
                out.append({
                    'url': url,
                    'filename': 'year-{}.json'.format(year),
                    'data_type': 'release_package',
                })

            return out
