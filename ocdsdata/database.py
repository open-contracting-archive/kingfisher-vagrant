import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
import datetime
import hashlib
import json
import os
import ocdsdata.maindatabase.config
import alembic.config


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


engine = sa.create_engine(ocdsdata.maindatabase.config.DB_URI, json_serializer=SetEncoder().encode)
metadata = sa.MetaData()

source_session_table = sa.Table('source_session', metadata,
                                sa.Column('id', sa.Integer, primary_key=True),
                                sa.Column('source_id', sa.Text, nullable=False),
                                sa.Column('data_version', sa.Text, nullable=False),
                                sa.Column('store_start_at', sa.DateTime(timezone=False), nullable=False),
                                sa.Column('store_end_at', sa.DateTime(timezone=False), nullable=True),
                                sa.Column('sample', sa.Boolean, nullable=False, default=False),
                                sa.UniqueConstraint('source_id', 'data_version', 'sample'),
                                )

source_session_file_status_table = sa.Table('source_session_file_status', metadata,
                                            sa.Column('id', sa.Integer, primary_key=True),
                                            sa.Column('source_session_id', sa.Integer,
                                                      sa.ForeignKey("source_session.id"), nullable=False),
                                            sa.Column('filename', sa.Text, nullable=True),
                                            sa.Column('store_start_at', sa.DateTime(timezone=False), nullable=True),
                                            sa.Column('store_end_at', sa.DateTime(timezone=False), nullable=True),
                                            sa.UniqueConstraint('source_session_id', 'filename'),
                                            )

data_table = sa.Table('data', metadata,
                      sa.Column('id', sa.Integer, primary_key=True),
                      sa.Column('hash_md5', sa.Text, nullable=False, unique=True),
                      sa.Column('data', JSONB, nullable=False),
                      )

package_data_table = sa.Table('package_data', metadata,
                              sa.Column('id', sa.Integer, primary_key=True),
                              sa.Column('hash_md5', sa.Text, nullable=False, unique=True),
                              sa.Column('data', JSONB, nullable=False),
                              )

release_table = sa.Table('release', metadata,
                         sa.Column('id', sa.Integer, primary_key=True),
                         sa.Column('source_session_file_status_id', sa.Integer,
                                   sa.ForeignKey("source_session_file_status.id"), nullable=False),
                         sa.Column('release_id', sa.Text, nullable=True),
                         sa.Column('ocid', sa.Text, nullable=True),
                         sa.Column('data_id', sa.Integer, sa.ForeignKey("data.id"), nullable=False),
                         sa.Column('package_data_id', sa.Integer, sa.ForeignKey("package_data.id"), nullable=False),
                         )

record_table = sa.Table('record', metadata,
                        sa.Column('id', sa.Integer, primary_key=True),
                        sa.Column('source_session_file_status_id', sa.Integer,
                                  sa.ForeignKey("source_session_file_status.id"), nullable=False),
                        sa.Column('ocid', sa.Text, nullable=True),
                        sa.Column('data_id', sa.Integer, sa.ForeignKey("data.id"), nullable=False),
                        sa.Column('package_data_id', sa.Integer, sa.ForeignKey("package_data.id"), nullable=False),
                        )

release_check_table = sa.Table('release_check', metadata,
                               sa.Column('id', sa.Integer, primary_key=True),
                               sa.Column('release_id', sa.Integer, sa.ForeignKey("release.id"), index=True,
                                         unique=True),
                               sa.Column('cove_output', JSONB, nullable=False)
                               )

record_check_table = sa.Table('record_check', metadata,
                              sa.Column('id', sa.Integer, primary_key=True),
                              sa.Column('record_id', sa.Integer, sa.ForeignKey("record.id"), index=True, unique=True),
                              sa.Column('cove_output', JSONB, nullable=False)
                              )


def delete_tables():
    engine.execute("drop table if exists record_check cascade")
    engine.execute("drop table if exists release_check cascade")
    engine.execute("drop table if exists record cascade")
    engine.execute("drop table if exists release cascade")
    engine.execute("drop table if exists package_data cascade")
    engine.execute("drop table if exists data cascade")
    engine.execute("drop table if exists source_session_file_status cascade")
    engine.execute("drop table if exists source_session cascade")
    engine.execute("drop table if exists alembic_version cascade")


def create_tables():
    alembicargs = [
        '--config', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mainalembic.ini')),
        '--raiseerr',
        'upgrade', 'head',
    ]
    alembic.config.main(argv=alembicargs)


def is_store_done(source_id, data_version, sample):
    with engine.begin() as connection:
        s = sa.sql.select([source_session_table]).where((source_session_table.c.source_id == source_id) &
                                                        (source_session_table.c.data_version == data_version) &
                                                        (source_session_table.c.sample == sample) &
                                                        (source_session_table.c.store_end_at != None))  # noqa
        result = connection.execute(s)
        return True if result.fetchone() else False


def is_store_in_progress(source_id, data_version, sample):
    with engine.begin() as connection:
        s = sa.sql.select([source_session_table]).where((source_session_table.c.source_id == source_id) &
                                                        (source_session_table.c.data_version == data_version) &
                                                        (source_session_table.c.sample == sample) &
                                                        (source_session_table.c.store_end_at == None))  # noqa
        result = connection.execute(s)
        return True if result.fetchone() else False


def get_id_of_store_in_progress(source_id, data_version, sample):
    with engine.begin() as connection:
        s = sa.sql.select([source_session_table]).where((source_session_table.c.source_id == source_id) &
                                                        (source_session_table.c.data_version == data_version) &
                                                        (source_session_table.c.sample == sample) &
                                                        (source_session_table.c.store_end_at == None))  # noqa
        result = connection.execute(s)
        return result.fetchone()[0]


def get_id_of_store(source_id, data_version, sample):
    with engine.begin() as connection:
        s = sa.sql.select([source_session_table]).where((source_session_table.c.source_id == source_id) &
                                                        (source_session_table.c.data_version == data_version) &
                                                        (source_session_table.c.sample == sample))
        result = connection.execute(s)
        return result.fetchone()[0]


def start_store(source_id, data_version, sample, metadata_db):
    # Note use of engine.begin means this happens in a DB transaction
    with engine.begin() as connection:

        if is_store_in_progress(source_id, data_version, sample):
            return get_id_of_store_in_progress(source_id, data_version, sample)
        else:
            value = connection.execute(source_session_table.insert(), {
                'source_id': source_id,
                'data_version': data_version,
                'sample': sample,
                'store_start_at': datetime.datetime.utcnow()
            })

            for file_info in metadata_db.list_filestatus():
                if not file_info['data_type'].startswith('meta'):
                    connection.execute(source_session_file_status_table.insert(), {
                        'source_session_id': value.inserted_primary_key[0],
                        'filename': file_info['filename'],
                    })

            return value.inserted_primary_key[0]


def end_store(source_session_id):
    with engine.begin() as connection:

        connection.execute(
            source_session_table.update().where(source_session_table.c.id == source_session_id).values(store_end_at=datetime.datetime.utcnow())
        )


def is_store_file_done(source_session_id, file_info):
    with engine.begin() as connection:
        s = sa.sql.select([source_session_file_status_table]).where((source_session_file_status_table.c.source_session_id == source_session_id) &
            (source_session_file_status_table.c.filename == file_info['filename']) &
            (source_session_file_status_table.c.store_end_at != None))  # noqa
        result = connection.execute(s)
        return True if result.fetchone() else False


def get_id_of_store_file(source_session_id, file_info):
    with engine.begin() as connection:
        s = sa.sql.select([source_session_file_status_table]).where((source_session_file_status_table.c.source_session_id == source_session_id) &
            (source_session_file_status_table.c.filename == file_info['filename']))  # noqa
        result = connection.execute(s)
        return result.fetchone()[0]


class add_file():
    connection = None
    transaction = None
    source_session_id = None
    source_session_file_status_id = None
    file_info = None

    def __init__(self, source_session_id, file_info):
        self.source_session_id = source_session_id
        self.file_info = file_info

    def __enter__(self):
        self.connection = engine.connect()
        self.transaction = self.connection.begin()

        # Look up the id for this file
        s = sa.sql.select([source_session_file_status_table])\
            .where((source_session_file_status_table.c.source_session_id == self.source_session_id) &
                   (source_session_file_status_table.c.filename == self.file_info['filename']))
        result = self.connection.execute(s)
        source_session_file_status_table_row = result.fetchone()

        self.source_session_file_status_id = source_session_file_status_table_row.id

        # mark file as started
        self.connection.execute(
            source_session_file_status_table.update()
            .where(source_session_file_status_table.c.id == self.source_session_file_status_id)
            .values(store_start_at=datetime.datetime.utcnow())
        )

        return self

    def __exit__(self, type, value, traceback):

        if type:

            self.transaction.rollback()

            self.connection.close()

        else:

            self.connection.execute(
                source_session_file_status_table.update()
                .where(source_session_file_status_table.c.id == self.source_session_file_status_id)
                .values(store_end_at=datetime.datetime.utcnow())
            )

            self.transaction.commit()

            self.connection.close()

    def insert_record(self, row, package_data):
        ocid = row.get('ocid')
        package_data_id = self.get_id_for_package_data(package_data)
        data_id = self.get_id_for_data(row)
        self.connection.execute(record_table.insert(), {
            'source_session_file_status_id': self.source_session_file_status_id,
            'ocid': ocid,
            'data_id': data_id,
            'package_data_id': package_data_id,
        })

    def insert_release(self, row, package_data):
        ocid = row.get('ocid')
        release_id = row.get('id')
        package_data_id = self.get_id_for_package_data(package_data)
        data_id = self.get_id_for_data(row)
        self.connection.execute(release_table.insert(), {
            'source_session_file_status_id': self.source_session_file_status_id,
            'release_id': release_id,
            'ocid': ocid,
            'data_id': data_id,
            'package_data_id': package_data_id,
        })

    def get_id_for_package_data(self, package_data):

        hash_md5 = get_hash_md5_for_data(package_data)

        s = sa.sql.select([package_data_table]).where(package_data_table.c.hash_md5 == hash_md5)
        result = self.connection.execute(s)
        existing_table_row = result.fetchone()
        if existing_table_row:
            return existing_table_row.id
        else:
            return self.connection.execute(package_data_table.insert(), {
                'hash_md5': hash_md5,
                'data': package_data,
            }).inserted_primary_key[0]

    def get_id_for_data(self, data):

        hash_md5 = get_hash_md5_for_data(data)

        s = sa.sql.select([data_table]).where(data_table.c.hash_md5 == hash_md5)
        result = self.connection.execute(s)
        existing_table_row = result.fetchone()
        if existing_table_row:
            return existing_table_row.id
        else:
            return self.connection.execute(data_table.insert(), {
                'hash_md5': hash_md5,
                'data': data,
            }).inserted_primary_key[0]


def get_hash_md5_for_data(data):
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.md5(data_str.encode('utf-8')).hexdigest()


def is_release_check_done(release_id):
    with engine.begin() as connection:
        s = sa.sql.select([release_check_table]).where(release_check_table.c.release_id == release_id)
        result = connection.execute(s)
        return True if result.fetchone() else False


def is_record_check_done(record_id):
    with engine.begin() as connection:
        s = sa.sql.select([record_check_table]).where(record_check_table.c.record_id == record_id)
        result = connection.execute(s)
        return True if result.fetchone() else False
