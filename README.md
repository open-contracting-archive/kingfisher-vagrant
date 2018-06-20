# ocdsdata

## Installation

Requirements: python3, postgresql-10

Set up a venv and install requirements:
```
virtualenv -p python3 .ve
source .ve/bin/activate
pip install -r requirements.txt
```

Example of creating an ocdsdata table and data:
```
sudo -u postgres createuser ocdsdata --pwprompt
sudo -u postgres createdb ocdsdata -O ocdsdata --encoding UTF8 --template template0 --lc-collate en_US.UTF-8 --lc-ctype en_US.UTF-8 
export DB_URI='postgres://ocdsdata:PASSWORD YOU CHOSE@localhost/ocdsdata'
alembic --config mainalembic.ini upgrade head
```

## Running

Run `ocdsdata-cli` with the argument of one of the publishers you want to fetch.

## Configuration

Database and configuration settings can be set using `~/.config/ocdsdata/config.ini` file. A sample one is included in the main directory.

You can also set the `DB_URI` enviromental variable to use a custom PostgreSQL server, the default is `postgres://ocdsdata:ocdsdata@localhost/ocdsdata`

## Run Tests

Run `py.test` from root directory.

## Main Database - Postgresql

Create DB Migrations with Alembic - http://alembic.zzzcomputing.com/en/latest/

    alembic --config=mainalembic.ini revision -m "message"

Add changes to new migration, and make sure you update database.py table structures and delete_tables to.

## Meta Database - SQLite

During Gather and Fetch stages, a local SQLite DB is used to track progress.

Create DB Migrations with Alembic - http://alembic.zzzcomputing.com/en/latest/

    alembic --config=metaalembic.ini revision -m "message"

Add changes to new migration, and make sure you update metadata_db.py table structures to.
