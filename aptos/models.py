import re

from copy import deepcopy

from .primitives import (
    Component,
    Creator
)
from . import visitors


class OpenAPIVisitor:

    def visit_specification(self, specification, *args):
        specification.paths.accept(self, *args)
        specification.components.accept(self, *args)
        return specification

    def visit_paths(self, paths, *args):
        for path, path_item in paths.items():
            paths[path] = path_item.accept(self, *args)

    def visit_path_item(self, path_item, *args):
        for operation in path_item.operations:
            operation = getattr(path_item, operation)
            if operation is None:
                continue
            operation.accept(self, *args)
        return path_item

    def visit_operation(self, operation, *args):
        operation.requestBody.accept(self, *args)
        operation.responses.accept(self, *args)
        operation.callbacks.accept(self, *args)
        return operation

    def visit_responses(self, responses, *args):
        for status, response in responses.items():
            responses[status] = response.accept(self, *args)

    def visit_response(self, response, *args):
        response.content.accept(self, *args)
        return response

    def visit_content(self, content, *args):
        for key, value in content.items():
            content[key] = value.accept(self, *args)

    def visit_media_type(self, media_type, *args):
        media_type.schema = media_type.schema.accept(self, *args)
        return media_type

    def visit_components(self, components, *args):
        for name, schema in components.get('schemas', {}).items():
            components['schemas'][name] = schema.accept(self, *args)
        components['responses'].accept(self, *args)

    def visit_request_body(self, request_body, *args):
        request_body.content.accept(self, *args)
        return request_body

    def visit_callbacks(self, callbacks, *args):
        for name, callback in callbacks.items():
            callbacks[name] = callback.accept(self, *args)

    def visit_callback(self, callback, *args):
        for name, path_item in callback.items():
            callback[name] = path_item.accept(self, *args)
        return callback


class TypeVisitor(OpenAPIVisitor, visitors.TypeVisitor):

    def visitUnknown(self, unknown, *args):
        context = deepcopy(self.context) if not args else args[0]
        match = re.match(r'^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?', unknown.value)  # noqa: E501
        if match is None:
            raise ValueError()
        group = match.group(9)
        if group == '/':
            return Creator.create(
                context.get('type')).fromJson(context).accept(self)
        components = group.split('/')[1:]
        context = context[components.pop(0)]
        unknown.value = '#/{}'.format('/'.join(components))
        return self.visitUnknown(unknown, context)


class OpenAPI(Component):

    def __init__(self, openapi='3.0.0', info=None, servers=None, paths=None,
                 components=None):
        self.openapi = openapi
        self.info = info
        self.servers = [] if servers is None else servers
        self.paths = paths
        self.components = components

    @classmethod
    def fromJson(cls, instance):
        instance = deepcopy(instance)
        instance['servers'] = list(
            Server.fromJson(server) for server in instance.get('servers', []))
        instance['paths'] = Paths.fromJson(instance.get('paths'))
        instance['components'] = Components.fromJson(
            instance.get('components'))
        return cls(**instance)

    def accept(self, visitor, *args):
        return visitor.visit_specification(self, *args)


class Components(dict, Component):

    @classmethod
    def fromJson(cls, instance=None):
        if instance is None:
            instance = {}
        for name, schema in instance.get('schemas', {}).items():
            instance['schemas'][name] = Creator.create(
                schema.get('type')).fromJson(schema)
        instance['responses'] = Responses.fromJson(instance.get('responses'))
        instance['callbacks'] = Callbacks.fromJson(instance.get('callbacks'))
        return cls(**instance)

    def accept(self, visitor, *args):
        return visitor.visit_components(self, *args)


class Server:

    def __init__(self, url='', description='', variables=None):
        self.url = url
        self.description = description
        self.variables = variables

    @classmethod
    def fromJson(cls, instance):
        return cls(**instance)


class Paths(dict, Component):

    @classmethod
    def fromJson(cls, instance=None):
        if instance is None:
            instance = {}
        for key, value in instance.items():
            instance[key] = PathItem.fromJson(value)
        return cls(instance)

    def accept(self, visitor, *args):
        return visitor.visit_paths(self, *args)


class PathItem(Component):

    operations = (
        'get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace',)

    def __init__(self, summary='', description='', get=None, put=None,
                 post=None, delete=None, options=None, head=None, patch=None,
                 trace=None, servers=None, parameters=None, **kwargs):
        self.ref = kwargs.get('$ref')
        self.summary = summary
        self.description = description
        self.get = get
        self.put = put
        self.post = post
        self.delete = delete
        self.options = options
        self.head = head
        self.patch = patch
        self.trace = trace
        self.servers = [] if servers is None else servers
        self.parameters = [] if parameters is None else parameters

    @classmethod
    def fromJson(cls, instance):
        for operation in cls.operations:
            if operation not in instance:
                continue
            instance[operation] = Operation.fromJson(instance.get(operation))
        instance['servers'] = list(
            Server.fromJson(server) for server in instance.get('servers', []))
        return cls(**instance)

    def accept(self, visitor, *args):
        return visitor.visit_path_item(self, *args)


class RequestBody(Component):

    def __init__(self, description='', content=None, required=False):
        self.description = description
        self.content = content
        self.required = required

    @classmethod
    def fromJson(cls, instance):
        instance['content'] = Content.fromJson(instance.get('content'))
        return cls(**instance)

    def accept(self, visitor, *args):
        return visitor.visit_request_body(self, *args)


class Operation:

    def __init__(self, tags=None, summary='', description='',
                 externalDocs=None, operationId='', parameters=None,
                 requestBody=None, responses=None, callbacks=None,
                 deprecated=False, security=None, servers=None):
        self.tags = [] if tags is None else tags
        self.summary = summary
        self.description = description
        self.externalDocs = externalDocs
        self.operationId = operationId
        self.parameters = [] if parameters is None else parameters
        self.requestBody = requestBody
        self.responses = responses
        self.callbacks = [] if callbacks is None else callbacks
        self.deprecated = deprecated
        self.security = [] if security is None else security
        self.servers = [] if servers is None else servers

    @classmethod
    def fromJson(cls, instance):
        instance['requestBody'] = RequestBody.fromJson(
            instance.get('requestBody', {}))
        instance['responses'] = Responses.fromJson(instance['responses'])
        instance['callbacks'] = Callbacks.fromJson(
            instance.get('callbacks', {}))
        return cls(**instance)

    def accept(self, visitor, *args):
        return visitor.visit_operation(self, *args)


class Responses(dict, Component):

    @classmethod
    def fromJson(cls, instance=None):
        if instance is None:
            instance = {}
        for key, value in instance.items():
            instance[key] = Response.fromJson(value)
        return cls(instance)

    def accept(self, visitor, *args):
        return visitor.visit_responses(self, *args)


class Response(Component):

    def __init__(self, description='', headers=None, content=None, links=None):
        self.description = description
        self.headers = headers
        self.content = content
        self.links = links

    @classmethod
    def fromJson(cls, instance):
        instance['content'] = Content.fromJson(instance.get('content'))
        return cls(**instance)

    def accept(self, visitor, *args):
        return visitor.visit_response(self, *args)


class Content(dict, Component):

    @classmethod
    def fromJson(cls, instance=None):
        if instance is None:
            instance = {}
        for key, value in instance.items():
            instance[key] = MediaType.fromJson(value)
        return cls(instance)

    def accept(self, visitor, *args):
        return visitor.visit_content(self, *args)


class Callbacks(dict, Component):

    @classmethod
    def fromJson(cls, instance=None):
        if instance is None:
            instance = {}
        for key, value in instance.items():
            instance[key] = Callback.fromJson(value)
        return cls(instance)

    def accept(self, visitor, *args):
        return visitor.visit_callbacks(self, *args)


class Callback(dict, Component):

    @classmethod
    def fromJson(cls, instance=None):
        if instance is None:
            instance = {}
        for key, value in instance.items():
            instance[key] = PathItem.fromJson(value)
        return cls(instance)

    def accept(self, visitor, *args):
        return visitor.visit_callback(self, *args)


class MediaType(Component):

    def __init__(self, schema=None, example=None, examples=None,
                 encoding=None):
        self.schema = schema
        self.example = example
        self.examples = examples
        self.encoding = encoding

    @classmethod
    def fromJson(cls, instance):
        if 'schema' in instance:
            schema = instance['schema']
            schema = Creator.create(schema.get('type')).fromJson(schema)
            instance['schema'] = schema
        return cls(**instance)

    def accept(self, visitor, *args):
        return visitor.visit_media_type(self, *args)
