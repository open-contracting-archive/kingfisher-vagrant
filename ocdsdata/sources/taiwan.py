from ocdsdata.base import Fetcher
import tempfile

class TaiwanFetcher(Fetcher):

    def __init__(self):

        output_directory = tempfile.mkdtemp('','taiwan')
        super().__init__('/', False, None, None, output_directory)


    def gather_all_download_urls(self):
        return [
            [
                'http://data.dsp.im/dataset/963c0c3d-49ac-4a66-b8fa-f56c8166bb91/resource/0abbe767-c940-49fe-80d3-bd68268f508e/download/2014-02.json',
                '2014-02.json',
                'json',
                []
            ]
        ]

