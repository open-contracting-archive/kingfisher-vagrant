Requirements and Install
========================

Requirements
------------

Requirements:

- python v3.5 or higher
- Postgresql v10 or higher


Installation
------------

Set up a venv and install requirements:

.. code-block:: shell-session

    virtualenv -p python3 .ve
    source .ve/bin/activate
    pip install -r requirements.txt
    pip install -e .



Database
------------

You need to create a UTF8 Postgresql database and create a user with write access.

Once you have created the database, you need to configure the tool to connect to the database.

You can see one way of doing that in the example below, but for other options see :doc:`config`.

You also have to run a command to create the tables in database.

You can see the command in the example below, but for more on that see :doc:`cli-upgrade-database`.

Example of creating an database user, database and setting up the schema:

.. code-block:: shell-session


    sudo -u postgres createuser ocdsdata --pwprompt
    sudo -u postgres createdb ocdsdata -O ocdsdata --encoding UTF8 --template template0 --lc-collate en_US.UTF-8 --lc-ctype en_US.UTF-8
    export DB_URI='postgres://ocdsdata:PASSWORD YOU CHOSE@localhost/ocdsdata'
    python ocdsdata-cli upgrade-database
