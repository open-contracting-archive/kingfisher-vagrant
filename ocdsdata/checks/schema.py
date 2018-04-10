import json
import operator
from collections import OrderedDict

import copy
import json_merge_patch
import jsonref
from sqlalchemy.exc import IntegrityError

from ocdsdata import util
from ocdsdata.database import insert_schema, create_tables, delete_schema

deref_schema = jsonref.load_uri('http://standard.open-contracting.org/schema/1__0__2/release-schema.json')


def flat_generator(properties, current_path=tuple(), deprecated_parent=False):
    for key, value in properties.items():
        deprecated = deprecated_parent
        prop_type = value.get('type')
        if value.get('deprecated'):
            deprecated = True
        elif getattr(value, '__reference__', None) and "deprecated" in value.__reference__:
            deprecated = True
        new_path = current_path + (key,)
        yield (new_path, deprecated)
        if 'object' in prop_type and 'properties' in value:
            yield from flat_generator(value['properties'], current_path=new_path, deprecated_parent=deprecated)
        if 'array' in prop_type and 'items' in value and 'object' in value['items']['type']:
            yield from flat_generator(value['items']['properties'], current_path=new_path,
                                           deprecated_parent=deprecated)


def insert_schema_path_table(version, uri):
    deref_schema = jsonref.load_uri(uri)
    fields = [{"path": "/".join(path), "deprecated": deprecated, "version": version, "url": uri} for path, deprecated in
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
    fields = [{"path": "/".join(path), "deprecated": deprecated, 'extension_name': extension_name,
               'extension_type': 'core' if core else 'community', 'url': uri, 'version': '1.1'} for path, deprecated in
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
    extension_url = "http://standard.open-contracting.org/extension_registry/master/extensions.json"
    schema_url = 'http://standard.open-contracting.org/schema/1__1__1/release-schema.json'
    data = util.get_url_request(extension_url)
    if data[1]:
        raise Exception('Error fetching the extensions')
    data = data[0].json()
    schema_obj = util.get_url_request(schema_url)[0].json()
    deref_schema = jsonref.load_uri(schema_url)
    fields = ["/".join(path) for path, deprecated in
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
        raise Exception("Exception getting extension dependency")
    data = data.json()
    dependencies = []
    if 'dependencies' in data:
        for dependency_url in data['dependencies']:
            print(dependency_url)
            dependency = util.get_url_request(dependency_url.replace('extension.json', 'release-schema.json'))[0].json()
            dependencies.append(dependency)
    return dependencies


def insert_all_schemas():
    pass

create_tables(True)
get_all_extensions()
#create_tables(True)
#insert_schema_path_table('1.1.1', 'http://standard.open-contracting.org/schema/1__1__1/release-schema.json')
