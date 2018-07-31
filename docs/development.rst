Developing this tool
====================

Run tests
---------

Run `py.test` from root directory.


Main Database - Postgresql
--------------------------

Create DB Migrations with Alembic - http://alembic.zzzcomputing.com/en/latest/

.. code-block:: shell-session

    alembic --config=mainalembic.ini revision -m "message"

Add changes to new migration, and make sure you update database.py table structures and delete_tables to.

Meta Database - SQLite
----------------------

During Gather and Fetch stages, a local SQLite DB is used to track progress.

Create DB Migrations with Alembic - http://alembic.zzzcomputing.com/en/latest/

.. code-block:: shell-session

    alembic --config=metaalembic.ini revision -m "message"

Add changes to new migration, and make sure you update metadata_db.py table structures to.

