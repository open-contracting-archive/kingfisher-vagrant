Command line tool - upgrade-database option
===========================================

This tool will setup from scratch or update to the latest versions the tables and structure in the Postgresql database.

The connection settings should be configured before running it.

.. code-block:: shell-session

    python ocdskingfisher-cli upgrade-database

If you want to delete all the existing tables before setting up empty tables, pass the `deletefirst` flag.

.. code-block:: shell-session

    python ocdskingfisher-cli upgrade-database --deletefirst
