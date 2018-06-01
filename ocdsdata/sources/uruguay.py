import feedparser
from ocdsdata.base import Source


class UruguaySource(Source):
    publisher_name = 'Uruguay'
    url = 'http://www.comprasestatales.gub.uy'
    source_id = 'uruguay'

    def gather_all_download_urls(self):
        feed = feedparser.parse('http://www.comprasestatales.gub.uy/ocds/rss')
        out = []
        for item in feed.entries:
            if self.sample and len(out) == 10:
                break
            out.append({
                'url': item.link,
                'filename': '%s.json' % item.guid.split('/')[-1],
                'data_type': 'release_package',
            })

        return out
