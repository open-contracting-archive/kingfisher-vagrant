# ocdsdata

## Installation

Requirements: python3, postgresql-10

Set up a venv and install requirements:
```
virtualenv -p python3 .ve
source .ve/bin/activate
_pip install -r requirements.txt
```

Example of creating an ocdsdata table and data:
```
sudo -u postgres createuser ocdsdata --pwprompt
sudo -u postgres createdb ocdsdata -O ocdsdata
export DB_URI='postgres://ocdsdata:PASSWORD YOU CHOSE@localhost/ocdsdata'
alembic --config mainalembic.ini upgrade head
```

## Running

Run `ocdsdata-cli` with the argument of one of the publishers you want to fetch.

Set the `DB_URI` enviromental variable to use a custom PostgreSQL server, the default is `postgres://ocdsdata:ocdsdata@localhost/ocdsdata`

## Run Tests

Run `py.test` from root directory.
