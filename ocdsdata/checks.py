from ocdsdata import database
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cove_ocds.settings")  # noqa
from cove_ocds.lib.api import ocds_json_output
import sqlalchemy as sa


def handle_package(package):
    return ocds_json_output('temp', None, None, convert=False, cache_schema=True, file_type='json', json_data=package)


def get_package_data(package_data_id):
    with database.engine.begin() as connection:
        s = sa.sql.select([database.package_data_table]) \
            .where(database.package_data_table.c.id == package_data_id)
        result = connection.execute(s)
        data_row = result.fetchone()
        return data_row['data']


def get_data(data_id):
    with database.engine.begin() as connection:
        s = sa.sql.select([database.data_table]) \
            .where(database.data_table.c.id == data_id)
        result = connection.execute(s)
        data_row = result.fetchone()
        return data_row['data']


def main():
    with database.engine.begin() as connection:
        connection.execute(database.release_check_table.delete())
        rows = connection.execute(database.release_table.select())
    for x, row in enumerate(rows):
        if x % 10 == 0:
            print('Checked {} releases'.format(x))
        package = get_package_data(row.package_data_id)
        package['releases'] = [get_data(row.data_id)]
        cove_output = handle_package(package)
        checks = [{
            'release_id': row.id,
            'cove_output': cove_output,
        }]
        with database.engine.begin() as connection:
            connection.execute(database.release_check_table.insert(), checks)

    with database.engine.begin() as connection:
        connection.execute(database.record_check_table.delete())
        rows = connection.execute(database.record_table.select())
    for x, row in enumerate(rows):
        if x % 10 == 0:
            print('Checked {} records '.format(x))
        package = get_package_data(row.package_data_id)
        package['records'] = [get_data(row.data_id)]
        cove_output = handle_package(package)
        checks = [{
            'record_id': row.id,
            'cove_output': cove_output,
        }]
        with database.engine.begin() as connection:
            connection.execute(database.record_check_table.insert(), checks)


if __name__ == '__main__':
    main()
