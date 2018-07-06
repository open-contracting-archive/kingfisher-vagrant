#!/usr/bin/env python

from distutils.core import setup

setup(name='ocdsdata',
      version='0.0',
      description='Get ocds data',
      author='Open Contracting',
      url='',
      packages=[
            'ocdsdata',
            'ocdsdata.sources',
            'ocdsdata.maindatabase',
            'ocdsdata.maindatabase.migrations',
            'ocdsdata.maindatabase.migrations.versions',
            'ocdsdata.metadatabase',
            'ocdsdata.metadatabase.migrations',
            'ocdsdata.metadatabase.migrations.versions',
            'ocdsdata.cli',
            'ocdsdata.cli.commands'
      ],
      scripts=['ocdsdata-cli'],
      package_data={'ocdsdata': [
              'maindatabase/migrations/script.py.mako'
          ]},
      include_package_data=True
      )
