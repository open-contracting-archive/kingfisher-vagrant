#!/usr/bin/env python
import os
from distutils.core import setup


here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(name='ocdsdata',
      version='0.0.1',
      description='Get, extract and process data in the Open Contracting Data Standard format',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Open Contracting Partnership, Open Data Services, Iniciativa Latinoamericana para los Datos Abiertos',
      author_email='data@open-contracting.org',
      url='https://open-contracting.org',
      license='BSD',
      packages=[
            'ocdsdata',
            'ocdsdata.sources',
            'ocdsdata.maindatabase',
            'ocdsdata.maindatabase.migrations',
            'ocdsdata.maindatabase.migrations.versions'
      ],
      install_requires=[],
      classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python :: Implementation :: CPython',
        'Intended Audience :: Financial and Insurance Industry',
      ],
      scripts=['ocdsdata-cli', 'ocdsdata-status'],
      package_data={'ocdsdata': [
              'maindatabase/migrations/script.py.mako'
          ]},
      include_package_data=True
      )
