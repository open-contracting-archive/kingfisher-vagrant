from ocdsdata.base import Fetcher
import requests


class UKContractsFinderFetcher(Fetcher):
    publisher_name = 'UK Contracts Finder'
    url = 'https://www.contractsfinder.service.gov.uk'
    source_id = 'uk_contracts_finder'

    def gather_all_download_urls(self):
        url = 'https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search?order=asc&page=1'
        r = requests.get(url)
        data = r.json()
        total = data['maxPage']
        out = []
        for page in range(1, total+1):
            out.append([
                'https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search?order=asc&page=%d' % page,
                'page%d.json' % page,
                'release_package',
                []
            ])
        return out
