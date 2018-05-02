import json
import operator
from sqlite3 import IntegrityError

import json_merge_patch
import jsonref

from ocdsdata import database, util
import os

from ocdsdata.database import insert_schema

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cove_ocds.settings")  # noqa
from cove_ocds.lib.api import ocds_json_output
import sqlalchemy as sa


def flat_generator(properties, current_path=tuple(), deprecated_parent=False):
    for key, value in properties.items():
        deprecated = deprecated_parent
        prop_type = value.get('type')
        if not prop_type:
            continue
        if value.get('deprecated'):
            deprecated = True
        elif getattr(value, '__reference__', None) and 'deprecated' in value.__reference__:
            deprecated = True
        new_path = current_path + (key,)
        yield (new_path, {'deprecated':deprecated, 'type':prop_type})
        if 'object' in prop_type and 'properties' in value:
            yield from flat_generator(value['properties'], current_path=new_path, deprecated_parent=deprecated)
        if 'array' in prop_type and 'items' in value and 'object' in value['items']['type']:
            yield from flat_generator(value['items']['properties'], current_path=new_path, deprecated_parent=deprecated)


def insert_schema_path_table(version, uri):
    deref_schema = jsonref.load_uri(uri)
    fields = [{'path': '/'.join(path), 'deprecated': info['deprecated'], 'version': version, 'url': uri, 'type': info['type']} for path, info in
              dict(flat_generator(deref_schema['properties'])).items()]
    sorted_x = sorted(fields, key=operator.itemgetter('path'))
    insert_schema(sorted_x)


def insert_extension_path_table(extension_name, uri, core, flatten_schema, schema_obj, extension_file_url):
    extension_data = util.get_url_request(uri)[0].json()
    dependencies = get_dependencies_extension(extension_file_url)
    if dependencies:
        get_dependencies_patch(extension_data, dependencies)
    merged = json_merge_patch.merge(schema_obj, extension_data)
    ref = jsonref.loads(json.dumps(merged))
    fields = [{'path': '/'.join(path), 'deprecated': info['deprecated'], 'extension_name': extension_name,
               'extension_type': 'core' if core else 'community', 'url': uri, 'version': '1.1', 'type': info['type']} for path, info in
              dict(flat_generator(ref['properties'])).items()]

    to_store = [x for x in fields if x['path'] not in flatten_schema]
    if to_store:
        try:
            insert_schema(to_store)
        except IntegrityError:
            print('Duplicate path - version')


def get_dependencies_patch(extension, dependencies):
    for dependency in dependencies:
        extension = json_merge_patch.merge(extension, dependency)


def get_all_extensions():
    extension_url = 'http://standard.open-contracting.org/extension_registry/master/extensions.json'
    schema_url = 'http://standard.open-contracting.org/schema/1__1__1/release-schema.json'
    data = util.get_url_request(extension_url)
    if data[1]:
        raise Exception('Error fetching the extensions')
    data = data[0].json()
    schema_obj = util.get_url_request(schema_url)[0].json()
    deref_schema = jsonref.load_uri(schema_url)
    fields = ['/'.join(path) for path, deprecated in
              dict(flat_generator(deref_schema['properties'])).items()]
    for extension in data['extensions']:
        core = extension['core']
        name = extension['name']['en']
        uri = extension['url']+'release-schema.json'
        extension_file_url = extension['url']+'extension.json'
        insert_extension_path_table(name, uri, core, fields, copy.deepcopy(schema_obj), extension_file_url)


def get_dependencies_extension(extension_url):
    data, errors = util.get_url_request(extension_url)
    if errors:
        raise Exception('Exception getting extension dependency')
    data = data.json()
    dependencies = []
    if 'dependencies' in data:
        for dependency_url in data['dependencies']:
            print(dependency_url)
            dependency = util.get_url_request(dependency_url.replace('extension.json', 'release-schema.json'))[0].json()
            dependencies.append(dependency)
    return dependencies


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
