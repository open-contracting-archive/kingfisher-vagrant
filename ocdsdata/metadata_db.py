import sqlalchemy as sa
import os


class MetadataDB(object):

    def __init__(self, directory_path = None):
        self.base_path = directory_path
        self.metadata_file = os.path.join(directory_path, "scrape_info.sqlite3")

        ## if no path, "debug mode" with in memory db and echo SQL generated.
        if (directory_path == None):
            self.engine = sa.create_engine("sqlite:///:memory:", echo=True)
        else:
            self.engine = sa.create_engine("sqlite:///"+self.metadata_file)
        self.metadata = sa.MetaData()


        self.fetch_session = sa.Table('scrape_session', self.metadata,
            sa.Column('data_version', sa.Text),
            sa.Column('publisher_name', sa.Text),
            sa.Column('base_url', sa.Text),

            sa.Column('gather_start_datetime', sa.DateTime, nullable=False),
            sa.Column('gather_finished_datetime', sa.DateTime, nullable=True),
            sa.Column('gather_errors', sa.Text, nullable=True),
            sa.Column('gather_success', sa.Boolean, nullable=False, default=False),

            sa.Column('fetch_start_datetime', sa.DateTime, nullable=False),
            sa.Column('fetch_finished_datetime', sa.DateTime, nullable=True),
            sa.Column('fetch_errors', sa.Text, nullable=True),
            sa.Column('fetch_success', sa.Boolean, nullable=False, default=False),

            sa.Column('store_start_datetime', sa.DateTime, nullable=False),
            sa.Column('store_finished_datetime', sa.DateTime, nullable=True),
            sa.Column('store_errors', sa.Text, nullable=True),
            sa.Column('store_success', sa.Boolean, nullable=False, default=False),
        )

        self.filestatus = sa.Table('filestatus', self.metadata,
            sa.Column('filename', sa.Text, primary_key=True),
            sa.Column('url', sa.Text, nullable=False),
            sa.Column('data_type', sa.Text, nullable=False),

            sa.Column('gather_error', sa.Text),

            sa.Column('fetch_start_datetime', sa.DateTime, nullable=False),
            sa.Column('fetch_finished_datetime', sa.DateTime, nullable=True),
            sa.Column('fetch_errors', sa.Text, nullable=True),
            sa.Column('fetch_success', sa.Boolean, nullable=False, default=False),

            sa.Column('store_start_datetime', sa.DateTime, nullable=False),
            sa.Column('store_finished_datetime', sa.DateTime, nullable=True),
            sa.Column('store_errors', sa.Text, nullable=True),
            sa.Column('store_success', sa.Boolean, nullable=False, default=False)
        )

        self.conn = self.engine.connect()
        self.metadata.create_all(self.engine)
