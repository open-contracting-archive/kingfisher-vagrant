import os
import pgpasslib

# Default database details
#
# This code is currently duplicated in ocdsdata/database.py and it would be good to remove that.
#
host = 'localhost'
port = '5432'
user = 'ocdsdata'
dbname = 'ocdsdata'

try:
    password = pgpasslib.getpass(host, port, user, dbname)

    database_uri = 'postgresql://{}:{}@{}/{}'.format(user, password, host, dbname)
except pgpasslib.FileNotFound:
    database_uri = 'postgresql://{}:{}@{}/{}'.format(user, 'ocdsdata', host, dbname)

DB_URI = os.environ.get('DB_URI', database_uri)
