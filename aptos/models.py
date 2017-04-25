from .primitives import TypeRegistry


class Swagger:

    def __init__(self, swagger='2.0', host='', basePath='', schemes=None,
                 consumes=None, produces=None, paths=None, definitions=None):
        self.swagger = swagger
        self.host = host
        self.basePath = basePath
        self.schemes = [] if schemes is None else list(schemes)
        self.consumes = [] if consumes is None else list(consumes)
        self.produces = [] if produces is None else list(produces)
        self.paths = paths
        self.definitions = {} if definitions is None else definitions


class Operation:

    def __init__(self, tags=None, summary='', description='',
                 externalDocs=None, operationId='', consumes=None,
                 produces=None, parameters=None, responses=None, schemes=None,
                 deprecated=False, security=None):
        self.tags = [] if tags is None else list(tags)
        self.summary = summary
        self.description = description
        self.externalDocs = externalDocs
        self.operationId = operationId
        self.consumes = [] if consumes is None else list(consumes)
        self.produces = [] if produces is None else list(produces)
        self.parameters = [] if parameters is None else list(parameters)
        self.responses = responses
        self.schemes = [] if schemes is None else list(schemes)
        self.deprecated = deprecated
        self.security = [] if security is None else list(security)

    @classmethod
    def fromJson(cls, instance, referrant=None):
        for status, response in instance['responses'].items():
            instance['responses'][status] = Response.fromJson(
                response, referrant=referrant)
        return cls(**instance)


class Response:

    def __init__(self, description='', schema=None, headers=None,
                 examples=None):
        self.description = description
        self.schema = {} if schema is None else schema
        self.headers = headers
        self.examples = examples

    @classmethod
    def fromJson(cls, instance, referrant=None):
        if 'schema' in instance:
            schema = instance['schema']
            schema = TypeRegistry.find(schema.get('type')).fromJson(schema)
            instance['schema'] = schema.resolve(referrant)
        return cls(**instance)
