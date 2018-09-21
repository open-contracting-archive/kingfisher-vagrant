import feedparser

from ocdskingfisher.base import Source


class UruguaySource(Source):
    publisher_name = 'Uruguay'
    url = 'http://www.comprasestatales.gub.uy'
    source_id = 'uruguay'

    def gather_all_download_urls(self):
        if self.sample:
            return [{
                'url': 'http://comprasestatales.gub.uy/ocds/rss/2017/12',
                'filename': 'sample.json',
                'data_type': 'meta',
                'priority': 10,
            }]

        out = []
        for year in range(2017, 2019):
            for month in range(1, 13):
                out.append({
                    'url': 'http://comprasestatales.gub.uy/ocds/rss/{}/{:02d}'.format(year, month),
                    'filename': 'year-{}-month-{:02d}.json'.format(year, month),
                    'data_type': 'meta',
                    'priority': 10,
                })
        return out

    def save_url(self, filename, data, file_path):
        if data['data_type'] == 'meta':

            feed = feedparser.parse(data['url'])
            additional = []
            for item in feed.entries:
                if self.sample and len(additional) == 10:
                    break
                additional.append({
                    'url': item.link,
                    'filename': '%s.json' % item.guid.split('/')[-1],
                    'data_type': 'release_package',
                })

            return self.SaveUrlResult(additional_files=additional)

        else:
            return super(UruguaySource, self).save_url(file_name=filename, data=data, file_path=file_path)
