import re

from copy import deepcopy


class Creator:

    @staticmethod
    def create(identifier):
        return {
            str: lambda identifier: {
                'array': Array,
                'boolean': Boolean,
                'integer': Integer,
                'object': Record,
                'string': String,
                'number': Number,
                'null': Null,
            }.get(identifier, Record),
            list: lambda identifier: Union,
            type(None): lambda identifier: Unknown,
        }[identifier.__class__](identifier)


class Translator:

    @staticmethod
    def translate(instance):
        return {
            dict: Record,
            list: Array,
            tuple: Array,
            str: String,
            int: Integer,
            float: Number,
            bool: Boolean,
            type(None): Null,
        }[instance.__class__]


class Component:

    def accept(self, visitor, *args):
        raise NotImplementedError()


class Primitive(Component):

    keywords = ('enum', 'const', 'type', 'allOf', 'anyOf', 'oneOf',)

    def __init__(self, enum=None, const=None, type=None, allOf=None,
                 anyOf=None, oneOf=None, definitions=None, title='',
                 description='', default=None, examples=None, format='',
                 **kwargs):
        # TODO: include `not`
        self.enum = [] if enum is None else list(set(enum))
        self.const = const
        self.type = type
        self.allOf = AllOf() if allOf is None else allOf
        self.anyOf = [] if anyOf is None else anyOf
        self.oneOf = [] if oneOf is None else oneOf
        self.definitions = (
            Definitions() if definitions is None else definitions)

        # Metadata keywords
        self.title = title
        self.description = description
        self.default = default
        self.examples = examples
        self.format = format

    @classmethod
    def fromJson(cls, instance):
        instance = deepcopy(instance)
        instance['enum'] = instance.get('enum', [])
        instance['allOf'] = AllOf.fromJson(instance.get('allOf'))
        instance['definitions'] = Definitions.fromJson(
            instance.get('definitions'))
        return cls(**instance)


class Definitions(Component, dict):

    @classmethod
    def fromJson(cls, definitions=None):
        if definitions is None:
            definitions = {}
        for name, member in definitions.items():
            member = Creator.create(member.get('type')).fromJson(member)
            definitions[name] = member
        return cls(definitions)

    def accept(self, visitor, *args):
        return visitor.visitDefinitions(self, *args)


class Properties(Component, dict):

    @classmethod
    def fromJson(cls, properties=None):
        if properties is None:
            properties = {}
        for name, member in properties.items():
            member = Creator.create(member.get('type')).fromJson(member)
            properties[name] = member
        return cls(properties)

    def accept(self, visitor, *args):
        return visitor.visitProperties(self, *args)


class Array(Primitive):
    """A JSON array."""

    keywords = ('additionalItems', 'items', 'maxItems', 'minItems',
                'uniqueItems',)

    class List:

        @classmethod
        def fromJson(cls, instance):
            return Creator.create(instance.get('type')).fromJson(instance)

    class Tuple:

        @classmethod
        def fromJson(cls, instance):
            return list(
                Creator.create(element.get('type')).fromJson(element)
                for element in instance)

    def __init__(self, additionalItems=None, items=None, maxItems=0,
                 minItems=0, uniqueItems=False, contains=None, **kwargs):
        super().__init__(**kwargs)
        self.additionalItems = (
            {} if additionalItems is None else additionalItems)
        self.items = items
        self.maxItems = maxItems
        self.minItems = minItems
        self.uniqueItems = uniqueItems
        self.contains = {} if contains is None else contains

    @classmethod
    def fromJson(cls, instance):
        instance = super().fromJson(instance)
        items = instance.items
        instance.items = {
            dict: Array.List.fromJson,
            list: Array.Tuple.fromJson,
        }[items.__class__](items)
        return instance

    def accept(self, visitor, *args):
        return visitor.visitArray(self, *args)


class AllOf(list):

    @classmethod
    def fromJson(cls, items=None):
        if items is None:
            items = []
        items = list(
            Creator.create(item.get('type')).fromJson(item) for item in items)
        return cls(items)

    def accept(self, visitor, *args):
        return visitor.visitAllOf(self, *args)


class Boolean(Primitive):
    """A JSON boolean."""

    keywords = ()

    def accept(self, visitor, *args):
        return visitor.visitBoolean(self, *args)


class Integer(Primitive):
    """A JSON number without a fraction or exponent part."""

    keywords = ('multipleOf', 'maximum', 'exclusiveMaximum', 'minimum',
                'exclusiveMinimum',)

    def __init__(self, multipleOf=0, maximum=0, exclusiveMaximum=False,
                 minimum=0, exclusiveMinimum=False, **kwargs):
        super().__init__(**kwargs)
        self.multipleOf = multipleOf
        self.maximum = maximum
        self.exclusiveMaximum = exclusiveMaximum
        self.minimum = minimum
        self.exclusiveMinimum = exclusiveMinimum

    def accept(self, visitor, *args):
        return visitor.visitInt(self, *args)


class Number(Primitive):
    """Any JSON number.  Number includes integer."""

    keywords = ('multipleOf', 'maximum', 'exclusiveMaximum', 'minimum',
                'exclusiveMinimum',)

    def __init__(self, multipleOf=0, maximum=None, exclusiveMaximum=False,
                 minimum=None, exclusiveMinimum=False, **kwargs):
        super().__init__(**kwargs)
        self.multipleOf = multipleOf
        self.maximum = maximum
        self.exclusiveMaximum = exclusiveMaximum
        self.minimum = minimum
        self.exclusiveMinimum = exclusiveMinimum

    def accept(self, visitor, *args):
        return visitor.visitLong(self, *args)


class Null(Primitive):
    """The JSON null value."""

    keywords = ()

    def accept(self, visitor, *args):
        return visitor.visitNull(self, *args)


class Record(Primitive):
    """A JSON object."""

    keywords = ('maxProperties', 'minProperties', 'required',
                'additionalProperties', 'properties', 'patternProperties',
                'dependencies', 'propertyNames',)

    def __init__(self, maxProperties=0, minProperties=0, required=None,
                 properties=None, patternProperties=None,
                 additionalProperties=None, dependencies=None,
                 propertyNames=None, **kwargs):
        super().__init__(**kwargs)
        self.maxProperties = maxProperties
        self.minProperties = minProperties
        self.required = [] if required is None else list(set(required))
        self.properties = properties
        self.patternProperties = (
            {} if patternProperties is None else dict(patternProperties))
        self.additionalProperties = (
            {} if additionalProperties is None else dict(additionalProperties))
        self.dependencies = dependencies
        self.propertyNames = (
            {} if propertyNames is None else dict(propertyNames))

    @classmethod
    def fromJson(cls, instance):
        instance = super().fromJson(instance)
        instance.properties = Properties.fromJson(instance.properties)
        return instance

    def accept(self, visitor, *args):
        return visitor.visitDeclared(self, *args)


class String(Primitive):
    """A JSON string."""

    keywords = ('maxLength', 'minLength', 'pattern',)

    def __init__(self, maxLength=0, minLength=0, pattern='', **kwargs):
        super().__init__(**kwargs)
        self.maxLength = maxLength
        self.minLength = minLength
        self.pattern = pattern

    def accept(self, visitor, *args):
        return visitor.visitString(self, *args)


class Union(Primitive):

    @classmethod
    def fromJson(cls, instance):
        instance['type'] = list(
            Creator.create(identifier).fromJson(instance)
            for identifier in instance['type'])
        return super().fromJson(instance)

    def accept(self, visitor, *args):
        return visitor.visitUnion(self, *args)


class Reference(Primitive):

    def __init__(self, **kwargs):
        value = kwargs['$ref']
        expression = re.compile(
            r'^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?')
        if expression.match(value) is None:
            raise ValueError()
        self.value = value

    def accept(self, visitor, *args):
        return visitor.visitUnknown(self, *args)


class Enumerated(Primitive):

    def accept(self, visitor, *args):
        return visitor.visitEnum(self, *args)


class Unknown:

    @classmethod
    def fromJson(cls, instance):
        return (
            Reference.fromJson(instance)
            if '$ref' in instance else Enumerated.fromJson(instance))
