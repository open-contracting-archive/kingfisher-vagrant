from ocdskingfisher import util
from ocdskingfisher.base import Source


class UgandaSource(Source):
    publisher_name = 'Uganda'
    url = 'http://gpp.ppda.go.ug'
    source_id = 'uganda'

    def gather_all_download_urls(self):
        tags = ['planning', 'tender', 'award', 'contract']
        out = []

        for tag in tags:
            if self.sample:
                out.append({
                    'url': 'http://gpp.ppda.go.ug/api/v1/releases?tag=%s&page=1' % tag,
                    'filename': 'tag%spage1.json' % tag,
                    'data_type': 'release_package',
                })
            else:
                r = util.get_url_request('http://gpp.ppda.go.ug/api/v1/releases?tag=%s&page=1' % tag)
                if r[1]:
                    raise Exception(r[1])
                r = r[0]
                data = r.json()
                last_page = data['pagination']['last_page']
                for page in range(1, last_page+1):
                    out.append({
                        'url': 'http://gpp.ppda.go.ug/api/v1/releases?tag=%s&page=%d' % (tag, page),
                        'filename': 'tag-%s-page-%d.json' % (tag, page),
                        'data_type': 'release_package',
                    })

        return out
