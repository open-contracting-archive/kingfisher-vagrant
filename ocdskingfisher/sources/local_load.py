import os
import glob
import shutil

import ocdskingfisher.base


class LocalLoadSource(ocdskingfisher.base.Source):
    publisher_name = 'Local Load'
    url = 'http://localhost/'
    source_id = 'local_load'
    argument_definitions = [
            {
                'name': 'localloaddirectory',
                'help': 'For Local Load source, specify a directory of files.',
            },
            {
                'name': 'localloaddatatype',
                'help': 'For Local Load source, specify type of data. ' +
                        ', '.join(ocdskingfisher.base.ALLOWED_DATA_TYPES_EXCLUDING_META),
            }
        ]

    def set_arguments(self, arguments):
        self.argument_directory = arguments.localloaddirectory
        self.argument_localloaddatatype = arguments.localloaddatatype

    def gather_all_download_urls(self):

        if not self.argument_directory:
            raise Exception("No Directory was passed!")

        if not os.path.isdir(self.argument_directory):
            raise Exception("The Directory passed could not be found!")

        if self.argument_localloaddatatype not in ocdskingfisher.base.ALLOWED_DATA_TYPES_EXCLUDING_META:
            raise Exception("The Data Type passed was not known!")

        out = []
        glob_path = os.path.join(self.argument_directory, '*')
        for file_path in glob.glob(os.path.join(glob_path)):
            if not self.sample or len(out) < 5:
                out.append({'url': file_path,
                            'filename': file_path.split('/')[-1],
                            'data_type': self.argument_localloaddatatype})
        return out

    def save_url(self, filename, data, file_path):
        shutil.copyfile(data['url'], file_path)
        return self.SaveUrlResult()
