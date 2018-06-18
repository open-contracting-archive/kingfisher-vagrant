import os
import pgpasslib
import configparser


DB_DEFAULTS = {
    'HOSTNAME': 'localhost',
    'PORT': '5432',
    'USERNAME': 'ocdsdata',
    'DBNAME': 'ocdsdata',
}

config = configparser.ConfigParser(defaults=DB_DEFAULTS)
## User level config file.
config.read('~/.config/ocdsdata/config.ini')


# Loads database details or defaults
host = config.get('HOSTNAME')
port = config.get('PORT')
user =  config.get('USERNAME')
dbname =  config.get('DBNAME')

try:
    password = pgpasslib.getpass(host, port, user, dbname)
    database_uri = 'postgresql://{}:{}@{}/{}'.format(user, password, host, dbname)
except pgpasslib.FileNotFound:
    database_uri = 'postgresql://{}:{}@{}/{}'.format(user, 'ocdsdata', host, dbname)

## Overwrites if DB_URI is specified.
DB_URI = os.environ.get('DB_URI', database_uri)
