from . import database
import os
from cove_ocds.lib.api import ocds_json_output


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cove_ocds.settings")


def handle_package(package):
    return ocds_json_output('temp', None, None, convert=False, cache_schema=True, file_type='json', json_data=package)


with database.engine.begin() as connection:
    connection.execute(database.releases_checks_table.delete())
    rows = connection.execute(database.releases_table.select())
for x, row in enumerate(rows):
    if x % 10 == 0:
        print('Checked {} releases'.format(x))
    package = row.package_data
    package['releases'] = [row.release]
    cove_output = handle_package(package)
    checks = [{
        'releases_id': row.id,
        'cove_output': cove_output,
    }]
    with database.engine.begin() as connection:
        connection.execute(database.releases_checks_table.insert(), checks)


with database.engine.begin() as connection:
    connection.execute(database.records_checks_table.delete())
    rows = connection.execute(database.records_table.select())
for x, row in enumerate(rows):
    if x % 10 == 0:
        print('Checked {} records '.format(x))
    package = row.package_data
    package['records'] = [row.record]
    cove_output = handle_package(package)
    checks = [{
        'records_id': row.id,
        'cove_output': cove_output,
    }]
    with database.engine.begin() as connection:
        connection.execute(database.records_checks_table.insert(), checks)
