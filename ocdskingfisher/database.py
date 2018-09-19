import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
import datetime
import hashlib
import json
import os
import ocdskingfisher.maindatabase.config
import alembic.config


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


_engine = None


# We must only create a connection if actually needed; sometimes people do operations that don't need a database
#   and in that case it shouldn't error that it can't connect to one!
def get_engine():
    global _engine
    if not _engine:
        _engine = sa.create_engine(ocdskingfisher.maindatabase.config.get_database_uri(), json_serializer=SetEncoder().encode)
    return _engine


# This can be called by scripts that know they are going to use the database later.
# It should setup any thing needed and raise any errors now.
def init():
    get_engine()


metadata = sa.MetaData()

collection_table = sa.Table('collection', metadata,
                            sa.Column('id', sa.Integer, primary_key=True),
                            sa.Column('source_id', sa.Text, nullable=False),
                            sa.Column('data_version', sa.Text, nullable=False),
                            sa.Column('gather_start_at', sa.DateTime(timezone=False), nullable=True),
                            sa.Column('gather_end_at', sa.DateTime(timezone=False), nullable=True),
                            sa.Column('fetch_start_at', sa.DateTime(timezone=False), nullable=True),
                            sa.Column('fetch_end_at', sa.DateTime(timezone=False), nullable=True),
                            sa.Column('store_start_at', sa.DateTime(timezone=False), nullable=False),
                            sa.Column('store_end_at', sa.DateTime(timezone=False), nullable=True),
                            sa.Column('sample', sa.Boolean, nullable=False, default=False),
                            sa.UniqueConstraint('source_id', 'data_version', 'sample'),
                            )

collection_file_status_table = sa.Table('collection_file_status', metadata,
                                        sa.Column('id', sa.Integer, primary_key=True),
                                        sa.Column('collection_id', sa.Integer,
                                                  sa.ForeignKey("collection.id"), nullable=False),
                                        sa.Column('filename', sa.Text, nullable=True),
                                        sa.Column('store_start_at', sa.DateTime(timezone=False), nullable=True),
                                        sa.Column('store_end_at', sa.DateTime(timezone=False), nullable=True),
                                        sa.Column('warnings', JSONB, nullable=True),
                                        sa.UniqueConstraint('collection_id', 'filename'),
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
                         sa.Column('collection_file_status_id', sa.Integer,
                                   sa.ForeignKey("collection_file_status.id"), nullable=False),
                         sa.Column('release_id', sa.Text, nullable=True),
                         sa.Column('ocid', sa.Text, nullable=True),
                         sa.Column('data_id', sa.Integer, sa.ForeignKey("data.id"), nullable=False),
                         sa.Column('package_data_id', sa.Integer, sa.ForeignKey("package_data.id"), nullable=False),
                         )

record_table = sa.Table('record', metadata,
                        sa.Column('id', sa.Integer, primary_key=True),
                        sa.Column('collection_file_status_id', sa.Integer,
                                  sa.ForeignKey("collection_file_status.id"), nullable=False),
                        sa.Column('ocid', sa.Text, nullable=True),
                        sa.Column('data_id', sa.Integer, sa.ForeignKey("data.id"), nullable=False),
                        sa.Column('package_data_id', sa.Integer, sa.ForeignKey("package_data.id"), nullable=False),
                        )

release_check_table = sa.Table('release_check', metadata,
                               sa.Column('id', sa.Integer, primary_key=True),
                               sa.Column('release_id', sa.Integer, sa.ForeignKey("release.id"), index=True,
                                         unique=False, nullable=False),
                               sa.Column('override_schema_version', sa.Text, nullable=True),
                               sa.Column('cove_output', JSONB, nullable=False),
                               sa.UniqueConstraint('release_id', 'override_schema_version',
                                                   name='ix_release_check_release_id_and_more')
                               )

record_check_table = sa.Table('record_check', metadata,
                              sa.Column('id', sa.Integer, primary_key=True),
                              sa.Column('record_id', sa.Integer, sa.ForeignKey("record.id"), index=True, unique=False,
                                        nullable=False),
                              sa.Column('override_schema_version', sa.Text, nullable=True),
                              sa.Column('cove_output', JSONB, nullable=False),
                              sa.UniqueConstraint('record_id', 'override_schema_version',
                                                  name='ix_record_check_record_id_and_more')
                              )

release_check_error_table = sa.Table('release_check_error', metadata,
                                     sa.Column('id', sa.Integer, primary_key=True),
                                     sa.Column('release_id', sa.Integer, sa.ForeignKey("release.id"), index=True,
                                               unique=False, nullable=False),
                                     sa.Column('override_schema_version', sa.Text, nullable=True),
                                     sa.Column('error',  sa.Text, nullable=False),
                                     sa.UniqueConstraint('release_id', 'override_schema_version',
                                                         name='ix_release_check_error_release_id_and_more')
                                     )

record_check_error_table = sa.Table('record_check_error', metadata,
                                    sa.Column('id', sa.Integer, primary_key=True),
                                    sa.Column('record_id', sa.Integer, sa.ForeignKey("record.id"), index=True,
                                              unique=False, nullable=False),
                                    sa.Column('override_schema_version', sa.Text, nullable=True),
                                    sa.Column('error',  sa.Text, nullable=False),
                                    sa.UniqueConstraint('record_id', 'override_schema_version',
                                                        name='ix_record_check_error_record_id_and_more')
                                    )


def delete_tables():
    engine = get_engine()
    engine.execute("drop table if exists record_check cascade")
    engine.execute("drop table if exists record_check_error cascade")
    engine.execute("drop table if exists release_check cascade")
    engine.execute("drop table if exists release_check_error cascade")
    engine.execute("drop table if exists record cascade")
    engine.execute("drop table if exists release cascade")
    engine.execute("drop table if exists package_data cascade")
    engine.execute("drop table if exists data cascade")
    engine.execute("drop table if exists collection_file_status cascade")
    engine.execute("drop table if exists source_session_file_status cascade")  # This is the old table name
    engine.execute("drop table if exists collection cascade")
    engine.execute("drop table if exists source_session cascade")  # This is the old table name
    engine.execute("drop table if exists alembic_version cascade")


def create_tables():
    alembicargs = [
        '--config', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mainalembic.ini')),
        '--raiseerr',
        'upgrade', 'head',
    ]
    alembic.config.main(argv=alembicargs)


def is_store_done(source_id, data_version, sample):
    with get_engine().begin() as connection:
        s = sa.sql.select([collection_table]).where((collection_table.c.source_id == source_id) &
                                                    (collection_table.c.data_version == data_version) &
                                                    (collection_table.c.sample == sample) &
                                                    (collection_table.c.store_end_at != None))  # noqa
        result = connection.execute(s)
        return True if result.fetchone() else False


def is_store_in_progress(source_id, data_version, sample):
    with get_engine().begin() as connection:
        s = sa.sql.select([collection_table]).where((collection_table.c.source_id == source_id) &
                                                    (collection_table.c.data_version == data_version) &
                                                    (collection_table.c.sample == sample) &
                                                    (collection_table.c.store_end_at == None))  # noqa
        result = connection.execute(s)
        return True if result.fetchone() else False


def get_id_of_store_in_progress(source_id, data_version, sample):
    with get_engine().begin() as connection:
        s = sa.sql.select([collection_table]).where((collection_table.c.source_id == source_id) &
                                                    (collection_table.c.data_version == data_version) &
                                                    (collection_table.c.sample == sample) &
                                                    (collection_table.c.store_end_at == None))  # noqa
        result = connection.execute(s)
        return result.fetchone()[0]


def get_id_of_store(source_id, data_version, sample):
    with get_engine().begin() as connection:
        s = sa.sql.select([collection_table]).where((collection_table.c.source_id == source_id) &
                                                    (collection_table.c.data_version == data_version) &
                                                    (collection_table.c.sample == sample))
        result = connection.execute(s)
        return result.fetchone()[0]


def is_check_done(collection_id):
    with get_engine().begin() as connection:

        # Have any releases NOT been done yet?
        sql = sa.sql.text("""SELECT count(*) FROM release
              JOIN collection_file_status ON collection_file_status.id = release.collection_file_status_id
              LEFT JOIN release_check ON release_check.release_id = release.id
              LEFT JOIN release_check_error ON release_check_error.release_id = release.id
              WHERE collection_file_status.collection_id = :id
               AND release_check_error.id IS NULL AND release_check.id IS NULL """)

        result = connection.execute(sql, id=collection_id)
        count = result.fetchone()[0]
        if count > 0:
            return False

        # Have any records NOT been done yet?
        sql = sa.sql.text("""SELECT count(*) FROM record
              JOIN collection_file_status ON collection_file_status.id = record.collection_file_status_id
              LEFT JOIN record_check ON record_check.record_id = record.id
              LEFT JOIN record_check_error ON record_check_error.record_id = record.id
              WHERE collection_file_status.collection_id = :id
               AND record_check_error.id IS NULL AND record_check.id IS NULL """)

        result = connection.execute(sql, id=collection_id)
        count = result.fetchone()[0]
        if count > 0:
            return False

        # Guess it's been done then!
        return True


def start_store(source_id, data_version, sample, metadata_db):
    # Note use of engine.begin means this happens in a DB transaction
    with get_engine().begin() as connection:

        if is_store_in_progress(source_id, data_version, sample):
            return get_id_of_store_in_progress(source_id, data_version, sample)
        else:
            metadatainfo = metadata_db.get_session()
            value = connection.execute(collection_table.insert(), {
                'source_id': source_id,
                'data_version': data_version,
                'sample': sample,
                'store_start_at': datetime.datetime.utcnow(),
                'gather_start_at': metadatainfo['gather_start_datetime'],
                'gather_end_at': metadatainfo['gather_finished_datetime'],
                'fetch_start_at': metadatainfo['fetch_start_datetime'],
                'fetch_end_at': metadatainfo['fetch_finished_datetime'],
            })

            for file_info in metadata_db.list_filestatus():
                if not file_info['data_type'].startswith('meta'):
                    warnings = json.loads(file_info['fetch_warnings']) if file_info['fetch_warnings'] else []
                    connection.execute(collection_file_status_table.insert(), {
                        'collection_id': value.inserted_primary_key[0],
                        'filename': file_info['filename'],
                        'warnings': warnings if len(warnings) > 0 else None
                    })

            return value.inserted_primary_key[0]


def end_store(collection_id):
    with get_engine().begin() as connection:

        connection.execute(
            collection_table.update().where(collection_table.c.id == collection_id).values(store_end_at=datetime.datetime.utcnow())
        )


def is_store_file_done(collection_id, file_info):
    with get_engine().begin() as connection:
        s = sa.sql.select([collection_file_status_table]).where((collection_file_status_table.c.collection_id == collection_id) &
                                                                (collection_file_status_table.c.filename == file_info['filename']) &
                                                                (collection_file_status_table.c.store_end_at != None))  # noqa
        result = connection.execute(s)
        return True if result.fetchone() else False


def get_id_of_store_file(collection_id, file_info):
    with get_engine().begin() as connection:
        s = sa.sql.select([collection_file_status_table]).where((collection_file_status_table.c.collection_id == collection_id) &
                                                                (collection_file_status_table.c.filename == file_info['filename']))  # noqa
        result = connection.execute(s)
        return result.fetchone()[0]


class add_file():
    connection = None
    transaction = None
    collection_id = None
    collection_file_status_id = None
    file_info = None

    def __init__(self, collection_id, file_info):
        self.collection_id = collection_id
        self.file_info = file_info

    def __enter__(self):
        self.connection = get_engine().connect()
        self.transaction = self.connection.begin()

        # Look up the id for this file
        s = sa.sql.select([collection_file_status_table])\
            .where((collection_file_status_table.c.collection_id == self.collection_id) &
                   (collection_file_status_table.c.filename == self.file_info['filename']))
        result = self.connection.execute(s)
        collection_file_status_table_row = result.fetchone()

        self.collection_file_status_id = collection_file_status_table_row.id

        # mark file as started
        self.connection.execute(
            collection_file_status_table.update()
            .where(collection_file_status_table.c.id == self.collection_file_status_id)
            .values(store_start_at=datetime.datetime.utcnow())
        )

        return self

    def __exit__(self, type, value, traceback):

        if type:

            self.transaction.rollback()

            self.connection.close()

        else:

            self.connection.execute(
                collection_file_status_table.update()
                .where(collection_file_status_table.c.id == self.collection_file_status_id)
                .values(store_end_at=datetime.datetime.utcnow())
            )

            self.transaction.commit()

            self.connection.close()

    def insert_record(self, row, package_data):
        ocid = row.get('ocid')
        package_data_id = self.get_id_for_package_data(package_data)
        data_id = self.get_id_for_data(row)
        self.connection.execute(record_table.insert(), {
            'collection_file_status_id': self.collection_file_status_id,
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
            'collection_file_status_id': self.collection_file_status_id,
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


def is_release_check_done(release_id, override_schema_version=None):
    with get_engine().begin() as connection:
        s = sa.sql.select([release_check_table])\
            .where((release_check_table.c.release_id == release_id) &
                   (release_check_table.c.override_schema_version == override_schema_version))
        result = connection.execute(s)
        if result.fetchone():
            return True

        s = sa.sql.select([release_check_error_table])\
            .where((release_check_error_table.c.release_id == release_id) &
                   (release_check_error_table.c.override_schema_version == override_schema_version))
        result = connection.execute(s)
        if result.fetchone():
            return True

    return False


def is_record_check_done(record_id, override_schema_version=None):
    with get_engine().begin() as connection:
        s = sa.sql.select([record_check_table])\
            .where((record_check_table.c.record_id == record_id) &
                   (record_check_table.c.override_schema_version == override_schema_version))
        result = connection.execute(s)
        if result.fetchone():
            return True

        s = sa.sql.select([record_check_error_table])\
            .where((record_check_error_table.c.record_id == record_id) &
                   (record_check_error_table.c.override_schema_version == override_schema_version))
        result = connection.execute(s)
        if result.fetchone():
            return True

    return False


def get_all_collections():
    out = []
    with ocdskingfisher.database.get_engine().begin() as connection:
        s = ocdskingfisher.database.sa.sql.select([ocdskingfisher.database.collection_table])
        for result in connection.execute(s):
            out.append({
                    "id": result['id'],
                    "source_id": result['source_id'],
                    "data_version": result['data_version'],
                    "sample": result['sample'],
                })
    return out
