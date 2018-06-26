import os
import glob
import inspect
import importlib

import ocdsdata.base


def gather_sources():
    sources = {}

    dir_path = os.path.dirname(os.path.realpath(__file__))
    sources_dir = os.path.join(dir_path, '..', 'ocdsdata', 'sources')
    for file in glob.glob(sources_dir + '/*.py'):
        module = importlib.import_module('ocdsdata.sources.' + file.split('/')[-1].split('.')[0])
        for item in dir(module):
            value = getattr(module, item)
            if inspect.isclass(value) and issubclass(value, ocdsdata.base.Source) and value is not ocdsdata.base.Source:
                sources[getattr(value, 'source_id')] = value
    return sources
