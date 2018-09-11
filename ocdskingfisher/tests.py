from os.path import join, exists
import tempfile
import pytest
from ocdskingfisher.base import Source
from ocdskingfisher import util
from ocdskingfisher import database
from ocdskingfisher import checks
from ocdskingfisher.metadata_db import MetadataDB
import sqlalchemy as sa

# Monkey patch to make tests run a lot faster
util.RETRY_TIME = 0.1


def setup_main_database():
    database.delete_tables()
    database.create_tables()


class EmptySource(Source):
    publisher_name = 'test'
    url = 'test_url'
    source_id = 'test'
    data_version = 'v1'

    def gather_all_download_urls(self):
        return []


class Basic(Source):
    publisher_name = 'test'
    url = 'test_url'
    source_id = 'test'
    data_version = 'v1'

    def gather_all_download_urls(self):
        yield {'url': 'https://raw.githubusercontent.com/open-contracting/sample-data/' +
                      '5bcbfcf48bf6e6599194b8acae61e2c6e8fb5009/fictional-example/1.1/ocds-213czf-000-00001-02-tender.json',
               'filename': 'file1.json',
               'data_type': 'release_package',
               'errors': []}


def test_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = Basic(tmpdir)
        metadata_file = join(tmpdir, 'test', 'v1', 'metadb.sqlite3')
        assert exists(metadata_file)

        metadata_db = MetadataDB(join(tmpdir, 'test', 'v1'))
        data = metadata_db.get_dict()
        assert data['publisher_name'] == 'test'
        assert data['base_url'] == 'test_url'
        assert data['session_start_datetime']
        del data, metadata_db

        fetcher.run_gather()
        metadata_db = MetadataDB(join(tmpdir, 'test', 'v1'))
        data = metadata_db.get_dict()
        assert data['gather_start_datetime']
        assert data['gather_finished_datetime']
        assert data['gather_success']
        del data, metadata_db

        fetcher.run_fetch()
        assert exists(join(tmpdir, 'test', 'v1', 'file1.json'))

        metadata_db = MetadataDB(join(tmpdir, 'test', 'v1'))
        data = metadata_db.get_dict()
        assert data['file_status']
        assert data['fetch_success']
        assert data['fetch_start_datetime']
        assert data['fetch_finished_datetime']
        del data, metadata_db

        setup_main_database()
        fetcher.run_store()


class Empty(Source):
    pass


def test_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(AttributeError):
            Empty(tmpdir)


class BadUrls(Source):
    publisher_name = 'test'
    url = 'test_url'
    source_id = 'test'
    data_version = 'v1'

    def gather_all_download_urls(self):
        yield {'url': 'https://thisaddressreallyshouldnotexists.com',
               'filename': 'file1.json',
               'data_type': 'releases',
               'errors': []}
        yield {'url': 'https://httpstat.us/500',
               'filename': 'file2.json',
               'data_type': 'releases',
               'errors': []}


def test_bad_url():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = BadUrls(tmpdir)
        fetcher.run_gather()
        fetcher.run_fetch()

        metadata_db = MetadataDB(join(tmpdir, 'test', 'v1'))
        data = metadata_db.get_dict()
        assert not data['fetch_success']
        for value in data['file_status'].values():
            assert not value['fetch_success']
            assert value['fetch_errors']


class BadFetchErrors(Source):
    publisher_name = 'test'
    url = 'test_url'
    source_id = 'test'
    data_version = 'v1'

    def gather_all_download_urls(self):
        yield {'url': 'https://raw.githubusercontent.com/open-contracting/sample-data/' +
                      '5bcbfcf48bf6e6599194b8acae61e2c6e8fb5009/fictional-example/1.1/ocds-213czf-000-00001-02-tender.json',
               'filename': 'file1.json',
               'data_type': 'releases',
               'errors': []}

    def save_url(self, file_name, data, file_path):
        return self.SaveUrlResult(errors=['A really bad error occured!'])


def test_bad_fetch_errors():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = BadFetchErrors(tmpdir)
        fetcher.run_gather()
        fetcher.run_fetch()

        metadata_db = MetadataDB(join(tmpdir, 'test', 'v1'))
        data = metadata_db.get_dict()
        assert data['gather_success']
        assert data['gather_finished_datetime']
        assert not data['fetch_success']
        assert not data['file_status']['file1.json']['fetch_success']
        assert data['file_status']['file1.json']['fetch_start_datetime']
        assert data['file_status']['file1.json']['fetch_finished_datetime']
        assert data['file_status']['file1.json']['fetch_errors'] == ['A really bad error occured!']
        assert data['file_status']['file1.json']['fetch_warnings'] == []

        with pytest.raises(Exception):
            fetcher.run_store()


class BadFetchWarnings(Source):
    publisher_name = 'test'
    url = 'test_url'
    source_id = 'test'
    data_version = 'v1'

    def gather_all_download_urls(self):
        yield {'url': 'https://raw.githubusercontent.com/open-contracting/sample-data/' +
                      '5bcbfcf48bf6e6599194b8acae61e2c6e8fb5009/fictional-example/1.1/ocds-213czf-000-00001-02-tender.json',
               'filename': 'file1.json',
               'data_type': 'releases',
               'errors': []}

    def save_url(self, file_name, data, file_path):
        return self.SaveUrlResult(warnings=['We found a control character!'])


def test_bad_fetch_warnings():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = BadFetchWarnings(tmpdir)
        fetcher.run_gather()
        fetcher.run_fetch()

        metadata_db = MetadataDB(join(tmpdir, 'test', 'v1'))
        data = metadata_db.get_dict()
        assert data['gather_success']
        assert data['gather_finished_datetime']
        assert data['fetch_success']
        assert data['file_status']['file1.json']['fetch_success']
        assert data['file_status']['file1.json']['fetch_start_datetime']
        assert data['file_status']['file1.json']['fetch_finished_datetime']
        assert data['file_status']['file1.json']['fetch_errors'] == []
        assert data['file_status']['file1.json']['fetch_warnings'] == ['We found a control character!']

        fetcher.run_store()


class BadFetchException(Source):
    publisher_name = 'test'
    url = 'test_url'
    source_id = 'test'
    data_version = 'v1'

    def gather_all_download_urls(self):
        yield {'url': 'https://raw.githubusercontent.com/open-contracting/sample-data/' +
                      '5bcbfcf48bf6e6599194b8acae61e2c6e8fb5009/fictional-example/1.1/ocds-213czf-000-00001-02-tender.json',
               'filename': 'file1.json',
               'data_type': 'releases',
               'errors': []}

    def save_url(self, file_name, data, file_path):
        raise Exception('Whoops')


def test_bad_fetch_exception():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = BadFetchException(tmpdir)
        fetcher.run_gather()
        fetcher.run_fetch()

        metadata_db = MetadataDB(join(tmpdir, 'test', 'v1'))
        data = metadata_db.get_dict()
        assert data['gather_success']
        assert data['gather_finished_datetime']
        assert not data['fetch_success']
        assert not data['file_status']['file1.json']['fetch_success']
        assert data['file_status']['file1.json']['fetch_start_datetime']
        assert data['file_status']['file1.json']['fetch_finished_datetime']
        assert data['file_status']['file1.json']['fetch_errors'] == ["Exception('Whoops',)"]

        with pytest.raises(Exception):
            fetcher.run_store()


class ExceptionGather(Source):
    publisher_name = 'test'
    url = 'test_url'
    source_id = 'test'
    data_version = 'v1'

    def gather_all_download_urls(self):
        raise IndexError


def test_exception_gather():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = ExceptionGather(tmpdir)
        fetcher.run_gather()

        metadata_db = MetadataDB(join(tmpdir, 'test', 'v1'))
        data = metadata_db.get_dict()
        assert not data['gather_success']
        assert data['gather_errors'] == 'IndexError()'
        assert data['gather_finished_datetime']
        assert data['gather_errors']

        with pytest.raises(Exception):
            fetcher.run_fetch()


def test_create_tables():
    setup_main_database()


def test_database_store():
    setup_main_database()
    with tempfile.TemporaryDirectory() as tmpdir:
        metadata_db = MetadataDB(tmpdir)
        metadata_db.create_session_metadata("Test", True, "http://www.test.com", "2018-01-01-10-00-00")

        # test this store
        assert not database.is_store_done("test_source", "2018-01-01-10-00-00", True)

        # start it!
        store_id = database.start_store("test_source", "2018-01-01-10-00-00", True, metadata_db)

        # test this store
        assert database.get_id_of_store("test_source", "2018-01-01-10-00-00", True) == store_id

        # end it!
        database.end_store(store_id)

        # test this store
        assert database.is_store_done("test_source", "2018-01-01-10-00-00", True)

        # test other stores aren't marked as done
        assert not database.is_store_done("test_source", "2018-01-01-10-00-00", False)  # Not a Sample
        assert not database.is_store_done("test_source", "2027-01-01-10-00-00", True)  # Different version
        assert not database.is_store_done("a_different_source", "2018-01-01-10-00-00", True)  # Different source


def test_database_store_file():
    setup_main_database()
    with tempfile.TemporaryDirectory() as tmpdir:
        metadata_db = MetadataDB(tmpdir)
        metadata_db.create_session_metadata("Test", True, "http://www.test.com", "2018-01-01-10-00-00")
        metadata_db.add_filestatus({'filename': 'test1.json', 'url': 'http://www.test.com', 'data_type': 'record_package'})

        # start it!
        store_id = database.start_store("test_source", "2018-01-01-10-00-00", True, metadata_db)

        # test
        file_id = database.get_id_of_store_file(store_id, {'filename': 'test1.json'})
        assert file_id == 1
        # Don't like hard coding ID in. Relies on DB assigning 1 to this new row. But I think we can assume that.


def test_checks_records():
    setup_main_database()
    with tempfile.TemporaryDirectory() as tmpdir:
        source = EmptySource(tmpdir)
        metadata_db = MetadataDB(tmpdir)
        metadata_db.create_session_metadata("Test", True, "http://www.test.com", "2018-01-01-10-00-00")
        metadata_db.add_filestatus({'filename': 'test1.json', 'url': 'http://www.test.com', 'data_type': 'record_package'})

        # store details
        source_session_id = database.start_store("test_source", "2018-01-01-10-00-00", True, metadata_db)
        for data in metadata_db.list_filestatus():
            with database.add_file(source_session_id, data) as database_file:
                database_file.insert_record({'record': 'totally'}, {'extensions': []})
        database.end_store(source_session_id)

        record_id = 1
        # Don't like hard coding ID in. Relies on DB assigning 1 to this new row. But I think we can assume that.

        # Test
        assert not database.is_record_check_done(record_id)
        assert not database.is_check_done(source_session_id)

        # check!
        for data in metadata_db.list_filestatus():
            checks.check_file(source, source_session_id, data)

        # Test
        assert database.is_record_check_done(record_id)
        assert database.is_check_done(source_session_id)

        with database.get_engine().begin() as connection:
            s = sa.sql.select([database.record_check_table])
            result = connection.execute(s)
            data = result.fetchone()

        assert data['cove_output']['file_type'] == 'json'
        assert len(data['cove_output']['validation_errors']) > 0


def test_checks_records_error():
    setup_main_database()
    with tempfile.TemporaryDirectory() as tmpdir:
        source = EmptySource(tmpdir)
        metadata_db = MetadataDB(tmpdir)
        metadata_db.create_session_metadata("Test", True, "http://www.test.com", "2018-01-01-10-00-00")
        metadata_db.add_filestatus({'filename': 'test1.json', 'url': 'http://www.test.com', 'data_type': 'record_package'})

        # store details
        source_session_id = database.start_store("test_source", "2018-01-01-10-00-00", True, metadata_db)
        for data in metadata_db.list_filestatus():
            with database.add_file(source_session_id, data) as database_file:
                database_file.insert_record({'record': 'totally'}, {'version': '0.1-does-not-exist', 'extensions': []})
        database.end_store(source_session_id)

        record_id = 1
        # Don't like hard coding ID in. Relies on DB assigning 1 to this new row. But I think we can assume that.

        # Test
        assert not database.is_record_check_done(record_id)
        assert not database.is_check_done(source_session_id)

        # check!
        for data in metadata_db.list_filestatus():
            checks.check_file(source, source_session_id, data)

        # Test
        assert database.is_record_check_done(record_id)
        assert database.is_check_done(source_session_id)

        with database.get_engine().begin() as connection:
            s = sa.sql.select([database.record_check_error_table])
            result = connection.execute(s)
            data = result.fetchone()

        assert 'The schema version in your data is not valid. Accepted values:' in data['error']


def test_checks_releases():
    setup_main_database()
    with tempfile.TemporaryDirectory() as tmpdir:
        source = EmptySource(tmpdir)
        metadata_db = MetadataDB(tmpdir)
        metadata_db.create_session_metadata("Test", True, "http://www.test.com", "2018-01-01-10-00-00")
        metadata_db.add_filestatus({'filename': 'test1.json', 'url': 'http://www.test.com', 'data_type': 'release_package'})

        # store details
        source_session_id = database.start_store("test_source", "2018-01-01-10-00-00", True, metadata_db)
        for data in metadata_db.list_filestatus():
            with database.add_file(source_session_id, data) as database_file:
                database_file.insert_release({'release': 'totally'}, {'extensions': []})
        database.end_store(source_session_id)

        release_id = 1
        # Don't like hard coding ID in. Relies on DB assigning 1 to this new row. But I think we can assume that.

        # Test
        assert not database.is_release_check_done(release_id)

        # check!
        for data in metadata_db.list_filestatus():
            checks.check_file(source, source_session_id, data)

        # Test
        assert database.is_release_check_done(release_id)

        with database.get_engine().begin() as connection:
            s = sa.sql.select([database.release_check_table])
            result = connection.execute(s)
            data = result.fetchone()

        assert data['cove_output']['file_type'] == 'json'
        assert len(data['cove_output']['validation_errors']) > 0


def test_checks_releases_error():
    setup_main_database()
    with tempfile.TemporaryDirectory() as tmpdir:
        source = EmptySource(tmpdir)
        metadata_db = MetadataDB(tmpdir)
        metadata_db.create_session_metadata("Test", True, "http://www.test.com", "2018-01-01-10-00-00")
        metadata_db.add_filestatus({'filename': 'test1.json', 'url': 'http://www.test.com', 'data_type': 'release_package'})

        # store details
        source_session_id = database.start_store("test_source", "2018-01-01-10-00-00", True, metadata_db)
        for data in metadata_db.list_filestatus():
            with database.add_file(source_session_id, data) as database_file:
                database_file.insert_release({'release': 'totally'}, {'version': '0.1-does-not-exist', 'extensions': []})
        database.end_store(source_session_id)

        release_id = 1
        # Don't like hard coding ID in. Relies on DB assigning 1 to this new row. But I think we can assume that.

        # Test
        assert not database.is_release_check_done(release_id)

        # check!
        for data in metadata_db.list_filestatus():
            checks.check_file(source, source_session_id, data)

        # Test
        assert database.is_release_check_done(release_id)

        with database.get_engine().begin() as connection:
            s = sa.sql.select([database.release_check_error_table])
            result = connection.execute(s)
            data = result.fetchone()

        assert 'The schema version in your data is not valid. Accepted values:' in data['error']


def test_database_get_hash_md5_for_data():
    assert database.get_hash_md5_for_data({'cats': 'many'}) == '538dd075f4a37d77be84c683b711d644'


def test_database_get_hash_md5_for_data2():
    assert database.get_hash_md5_for_data({'cats': 'none'}) == '562c5f4221c75c8f08da103cc10c4e4c'


def test_metadatabase_store():
    setup_main_database()
    with tempfile.TemporaryDirectory() as tmpdir:
        metadata_db = MetadataDB(tmpdir)
        metadata_db.create_session_metadata("Test", True, "http://www.test.com", "2018-01-01-10-00-00")

        # No files
        assert not metadata_db.has_filestatus_filename('file1.json')

        # Add files
        metadata_db.add_filestatus({
            'url': 'https://raw.githubusercontent.com/open-contracting/sample-data/' +
                   '5bcbfcf48bf6e6599194b8acae61e2c6e8fb5009/fictional-example/1.1/ocds-213czf-000-00001-02-tender.json',
            'filename': 'file1.json',
            'data_type': 'releases'})

        # Check file
        assert metadata_db.has_filestatus_filename('file1.json')

        assert metadata_db.compare_filestatus_to_database({
            'url': 'https://raw.githubusercontent.com/open-contracting/sample-data/' +
                   '5bcbfcf48bf6e6599194b8acae61e2c6e8fb5009/fictional-example/1.1/ocds-213czf-000-00001-02-tender.json',
            'filename': 'file1.json',
            'data_type': 'releases'})

        assert metadata_db.compare_filestatus_to_database({
            'url': 'https://raw.githubusercontent.com/open-contracting/sample-data/' +
                   '5bcbfcf48bf6e6599194b8acae61e2c6e8fb5009/fictional-example/1.1/ocds-213czf-000-00001-02-tender.json',
            'filename': 'file1.json',
            'data_type': 'releases',
            'priority': 1})

        assert metadata_db.compare_filestatus_to_database({
            'url': 'https://raw.githubusercontent.com/open-contracting/sample-data/' +
                   '5bcbfcf48bf6e6599194b8acae61e2c6e8fb5009/fictional-example/1.1/ocds-213czf-000-00001-02-tender.json',
            'filename': 'file1.json',
            'data_type': 'releases',
            'encoding': 'utf-8'})

        #  .... different data_type
        assert not metadata_db.compare_filestatus_to_database({
            'url': 'https://raw.githubusercontent.com/open-contracting/sample-data/' +
                   '5bcbfcf48bf6e6599194b8acae61e2c6e8fb5009/fictional-example/1.1/ocds-213czf-000-00001-02-tender.json',
            'filename': 'file1.json',
            'data_type': 'releases-package'})

        # .... different url
        assert not metadata_db.compare_filestatus_to_database({
            'url': 'https://www.google.com/',
            'filename': 'file1.json',
            'data_type': 'releases'})

        # .... different priority
        assert not metadata_db.compare_filestatus_to_database({
            'url': 'https://raw.githubusercontent.com/open-contracting/sample-data/' +
                   '5bcbfcf48bf6e6599194b8acae61e2c6e8fb5009/fictional-example/1.1/ocds-213czf-000-00001-02-tender.json',
            'filename': 'file1.json',
            'data_type': 'releases',
            'priority': 10})

        # .... different encoding
        assert not metadata_db.compare_filestatus_to_database({
            'url': 'https://raw.githubusercontent.com/open-contracting/sample-data/' +
                   '5bcbfcf48bf6e6599194b8acae61e2c6e8fb5009/fictional-example/1.1/ocds-213czf-000-00001-02-tender.json',
            'filename': 'file1.json',
            'data_type': 'releases',
            'encoding': 'ascii'})


def test_control_code_to_filter_out_to_human_readable():
    for control_code_to_filter_out in util.control_codes_to_filter_out:
        # This test just calls it and make sure it runs without crashing
        # (some code was crashing, so wanted test to check all future values of control_codes_to_filter_out)
        print(util.control_code_to_filter_out_to_human_readable(control_code_to_filter_out))
