import json

from urllib.parse import urlparse

from .models import Operation, Swagger
from .primitives import Object


def read(fp):
    try:
        specification = json.loads(fp.read())
    finally:
        fp.close()

    definitions = specification['definitions']

    # TODO: variable name 'definition'?
    for definition, schema in definitions.items():
        if 'properties' not in schema:
            continue  # not an object
        definitions[definition] = Object.load(schema, referrant=specification)

    paths = specification['paths']

    for path, operations in paths.items():
        for method, operation in operations.items():
            paths[path][method] = Operation.load(
                operation, referrant=specification)

    return Swagger(
        host=specification.get('host'), basePath=specification.get('basePath'),
        paths=paths, definitions=definitions)


def parse_from(response, specification, encoding='utf-8'):
    path = urlparse(response.geturl()).path
    if specification.basePath in path:
        path = path.replace(specification.basePath, '')
    instance = json.loads(response.read().decode(encoding))
    operation = specification.paths[path][response._method.lower()]
    schema = operation.responses.get(str(response.status), 'default').schema
    schema = schema(instance)
    schema.default = instance
    return schema
