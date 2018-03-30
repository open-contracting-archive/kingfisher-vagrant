import sqlalchemy as sa
import os
from sqlalchemy.dialects.postgresql import JSONB

DB_URI = os.environ.get('DB_URI', 'postgres://ocdsdata:ocdsdata@localhost/ocdsdata')

engine = sa.create_engine(DB_URI)
metadata = sa.MetaData()

releases_table = sa.Table('releases', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('output_directory', sa.Text, nullable=False),
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
    sa.Column('output_directory', sa.Text, nullable=False),
    sa.Column('file', sa.Text, nullable=False),
    sa.Column('publisher_name', sa.Text),
    sa.Column('url', sa.Text),
    sa.Column('package_data', JSONB),
    sa.Column('ocid', sa.Text),
    sa.Column('record', JSONB, nullable=False),
)


def create_tables(drop=True):
    with engine.begin() as connection:
        if drop:
            metadata.drop_all(engine)
        metadata.create_all(engine)

def delete_releases(output_directory):
    with engine.begin() as connection:
        connection.execute(releases_table.delete().where(releases_table.c.output_directory == output_directory))

def delete_records(output_directory):
    with engine.begin() as connection:
        connection.execute(records_table.delete().where(records_table.c.output_directory == output_directory))

def insert_releases(releases):
    with engine.begin() as connection:
        connection.execute(releases_table.insert(),
                           releases)

def insert_records(records):
    with engine.begin() as connection:
        connection.execute(records_table.insert(),
                           records)




