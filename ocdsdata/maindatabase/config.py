import os
import pgpasslib
import configparser

config = configparser.ConfigParser()
## User level config file.
config.read('~/.config/ocdsdata/config.ini')

# Loads database details or defaults
host = config.get('HOSTNAME', 'localhost')
port = config.get('PORT', '5432')
user =  config.get('USERNAME','ocdsdata')
dbname =  config.get('DBNAME','ocdsdata')

try:
    password = pgpasslib.getpass(host, port, user, dbname)
    database_uri = 'postgresql://{}:{}@{}/{}'.format(user, password, host, dbname)
except pgpasslib.FileNotFound:
    database_uri = 'postgresql://{}:{}@{}/{}'.format(user, 'ocdsdata', host, dbname)

## Overwrites if DB_URI is specified.
DB_URI = os.environ.get('DB_URI', database_uri)
