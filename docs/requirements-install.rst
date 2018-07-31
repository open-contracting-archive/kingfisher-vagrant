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

Example of creating an database user, database and setting up the schema:

.. code-block:: shell-session


    sudo -u postgres createuser ocdsdata --pwprompt
    sudo -u postgres createdb ocdsdata -O ocdsdata --encoding UTF8 --template template0 --lc-collate en_US.UTF-8 --lc-ctype en_US.UTF-8
    export DB_URI='postgres://ocdsdata:PASSWORD YOU CHOSE@localhost/ocdsdata'
    python ocdsdata-cli upgrade-database


