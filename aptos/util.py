import json

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
