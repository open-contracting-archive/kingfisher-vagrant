Configuration
=============

Main database Configuration
---------------------------

Postgresql Database settings can be set using a `~/.config/ocdskingfisher/config.ini` file. A sample one is included in the
main directory.


.. code-block:: ini

    [DBHOST]
    HOSTNAME = localhost
    PORT = 5432
    USERNAME = ocdsdata
    PASSWORD = FIXME
    DBNAME = ocdsdata


It will also attempt to load the password from a `~/.pgpass` file, if one is present.

You can also set the `DB_URI` environmental variable to use a custom PostgreSQL server, for example
`postgresql://user:password@localhost:5432/dbname`.

The order of precedence is (from least-important to most-important):

  -  config file
  -  password from `~/.pgpass`
  -  environmental variable

Disk Configuration
------------------

This tool will save files to disk as it works.

Where it saves them can be set using  a `~/.config/ocdskingfisher/config.ini` file. A sample one is included in the
main directory.


.. code-block:: ini

    [DATA]
    DIR = /var/ocdskingfisher/data


You can also set the `KINGFISHER_DATA_DIR` environmental variable to use a custom directory.

The order of precedence is (from least-important to most-important):

  -  config file
  -  environmental variable


Logging Configuration
---------------------

This tool will provide additional logging information using the standard Python logging module, with loggers in the "ocdskingfisher"
namespace.

When using the command line tool, it can be configured by setting a `~/.config/ocdskingfisher/logging.json` file.
A sample one is included in the main directory.


Backwards compatibility
-----------------------

For backwards compatibility with older versions, `~/.config/ocdsdata/config.ini` and `~/.config/ocdsdata/logging.json` will also work.

