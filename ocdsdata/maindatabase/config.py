import os
import sys
import pgpasslib
import configparser


def __gen_dburi(user, password, host, port, dbname):
    return 'postgresql://{}:{}@{}:{}/{}'.format(user, password, host, port, dbname)


def get_database_uri():
    if os.environ.get('DB_URI'):
        return os.environ.get('DB_URI')

    config = configparser.ConfigParser()
    # User level config file.
    read_files = config.read(os.path.expanduser('~/.config/ocdsdata/config.ini'))

    if len(read_files) == 0:
        print("There are no config files nor DB_URI, therefore we cannot start.")
        quit(-1)

    # Loads database details or defaults
    host = config.get('DBHOST', 'HOSTNAME')
    port = config.get('DBHOST', 'PORT')
    user = config.get('DBHOST', 'USERNAME')
    dbname = config.get('DBHOST', 'DBNAME')
    dbpass = config.get('DBHOST', 'PASSWORD', fallback='')

    try:
        fetched_pass = pgpasslib.getpass(host, port, user, dbname)
        password = fetched_pass if fetched_pass else dbpass
        database_uri = __gen_dburi(user, password, host, port, dbname)
    except pgpasslib.FileNotFound:
        # Fail silently when no files found.
        database_uri = __gen_dburi(user, dbpass, host, port, dbname)
    except pgpasslib.InvalidPermissions:
        print("Your pgpass file has the wrong permissions, for your safety this file will be ignored. Please fix the permissions and try again.")
        database_uri = __gen_dburi(user, dbpass, host, port, dbname)
    except pgpasslib.PgPassException:
        print("Unexpected error:", sys.exc_info()[0])
        database_uri = __gen_dburi(user, dbpass, host, port, dbname)

    return database_uri
