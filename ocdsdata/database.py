import sqlalchemy as sa
import json
import os
from sqlalchemy.dialects.postgresql import JSONB
from os.path import expanduser
import pgpasslib

# Default database details
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


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


engine = sa.create_engine(DB_URI, json_serializer=SetEncoder().encode)
metadata = sa.MetaData()

releases_table = sa.Table('releases', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('source_id', sa.Text, nullable=False),
    sa.Column('data_version', sa.Text, nullable=False),
    sa.Column('sample', sa.Boolean, nullable=False),
    sa.Column('file', sa.Text, nullable=False),
    sa.Column('publisher_name', sa.Text),
    sa.Column('url', sa.Text),
    sa.Column('package_data', JSONB),
    sa.Column('release_id', sa.Text),
    sa.Column('ocid', sa.Text),
    sa.Column('release', JSONB, nullable=False),
)

records_table = sa.Table('records', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('source_id', sa.Text, nullable=False),
    sa.Column('data_version', sa.Text, nullable=False),
    sa.Column('sample', sa.Boolean, nullable=False),
    sa.Column('file', sa.Text, nullable=False),
    sa.Column('publisher_name', sa.Text),
    sa.Column('url', sa.Text),
    sa.Column('package_data', JSONB),
    sa.Column('ocid', sa.Text),
    sa.Column('record', JSONB, nullable=False),
)

releases_checks_table = sa.Table('releases_checks', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('releases_id', sa.Integer, index=True, unique=True),
    sa.Column('cove_output', JSONB, nullable=False)
)

records_checks_table = sa.Table('records_checks', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('records_id', sa.Integer, index=True, unique=True),
    sa.Column('cove_output', JSONB, nullable=False)
)


def create_tables(drop=True):
    with engine.begin() as connection:
        if drop:
            metadata.drop_all(engine)
        metadata.create_all(engine)

def delete_releases(source_id):
    with engine.begin() as connection:
        connection.execute(releases_table.delete().where(releases_table.c.source_id == source_id))

def delete_records(source_id):
    with engine.begin() as connection:
        connection.execute(records_table.delete().where(records_table.c.source_id == source_id))

def insert_releases(releases):
    with engine.begin() as connection:
        connection.execute(releases_table.insert(),
                           releases)

def insert_records(records):
    with engine.begin() as connection:
        connection.execute(records_table.insert(),
                           records)




