from .primitives import TypeFactory


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
        if definitions is None:
            definitions = {}
        self.definitions = definitions


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
    def load(cls, instance, referrant=None):
        for status, response in instance['responses'].items():
            instance['responses'][status] = Response.load(
                response, referrant=referrant)
        return cls(**instance)


class Response:
    def __init__(self, description='', schema=None, headers=None,
                 examples=None):
        self.description = description
        if schema is None:
            schema = {}
        self.schema = schema
        self.headers = headers
        self.examples = examples

    @classmethod
    def load(cls, instance, referrant):
        if 'schema' in instance:
            schema = instance['schema']
            schema = TypeFactory.construct_type(
                schema.get('type'), schema.get('format', '')).load(schema)
            instance['schema'] = schema.resolve(referrant)
        return cls(**instance)
