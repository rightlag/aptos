class JSONSchema:

    types = (
        'array', 'boolean', 'integer', 'number', 'null', 'object', 'string',)


class EntityMapperTranslator:

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


class Component:

    def accept(self, visitor):
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
        self.allOf = [] if allOf is None else list(allOf)
        self.anyOf = [] if anyOf is None else list(anyOf)
        self.oneOf = [] if oneOf is None else list(oneOf)
        self.definitions = {} if definitions is None else dict(definitions)

        # Metadata keywords
        self.title = title
        self.description = description
        self.default = default
        self.examples = examples
        self.format = format

    @classmethod
    def fromJson(cls, instance, referrant=None):
        if 'definitions' in instance:
            for name, definition in instance['definitions'].items():
                instance['definitions'][name] = Record.fromJson(
                    definition, referrant=referrant)
        if 'allOf' in instance:
            properties = {}
            for schema in instance.get('allOf', []):
                schema = Creator.create(schema.get('type')).fromJson(
                    schema, referrant=referrant)
                schema = schema.resolve(referrant=referrant)
                properties.update(schema.properties)
            instance['properties'] = properties
        return cls(**instance)

    def __call__(self, instance):
        if self.enum:
            assert instance in self.enum
        # TODO: validation for `type`, `allOf`, `anyOf`, `oneOf`, and
        # `definitions`
        return self


class Array(Primitive):
    """A JSON array."""

    keywords = ('additionalItems', 'items', 'maxItems', 'minItems',
                'uniqueItems',)

    def __init__(self, additionalItems=None, items=None, maxItems=0,
                 minItems=0, uniqueItems=False, **kwargs):
        super().__init__(**kwargs)
        self.additionalItems = additionalItems
        self.items = items
        self.maxItems = maxItems
        self.minItems = minItems
        self.uniqueItems = uniqueItems

    @classmethod
    def fromJson(cls, instance, referrant=None):
        instance = super().fromJson(instance, referrant=referrant)
        items = instance.items
        instance.items = Creator.create(items.get('type')).fromJson(
            items, referrant=referrant)
        return instance

    def __call__(self, instance):
        for child in instance:
            self.items(child)
        if not self.additionalItems and isinstance(self.items, Array):
            assert len(instance) <= self.items
        if self.maxItems:
            assert len(instance) <= self.maxItems
        assert len(instance) >= self.minItems
        if self.uniqueItems:
            assert len(list(set(instance))) == len(instance)
        return super().__call__(instance)


class Boolean(Primitive):
    """A JSON boolean."""

    keywords = ()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


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

    def __call__(self, instance):
        if self.multipleOf:
            assert isinstance((instance / self.multipleOf), int)
        if self.exclusiveMaximum:
            if self.maximum:
                assert instance < self.maximum
        else:
            if self.maximum:
                assert instance <= self.maximum
        if self.exclusiveMinimum:
            assert instance > self.minimum
        else:
            assert instance >= self.minimum
        return super().__call__(instance)


class Number(Primitive):
    """Any JSON number.  Number includes integer."""

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

    def __call__(self, instance):
        if self.multipleOf:
            assert isinstance((instance / self.multipleOf), int)
        if self.exclusiveMaximum:
            if self.maximum:
                assert instance < self.maximum
        else:
            if self.maximum:
                assert instance <= self.maximum
        if self.exclusiveMinimum:
            assert instance > self.minimum
        else:
            assert instance >= self.minimum
        return super().__call__(instance)


class Null(Primitive):
    """The JSON null value."""

    keywords = ()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Record(Primitive):
    """A JSON object."""

    keywords = ('maxProperties', 'minProperties', 'required',
                'additionalProperties', 'properties', 'patternProperties',
                'dependencies',)

    def __init__(self, maxProperties=0, minProperties=0, required=None,
                 additionalProperties=None, properties=None,
                 patternProperties=None, dependencies=None, **kwargs):
        super().__init__(**kwargs)
        self.maxProperties = maxProperties
        self.minProperties = minProperties
        self.required = [] if required is None else list(set(required))
        self.additionalProperties = additionalProperties
        self.properties = {} if properties is None else dict(properties)
        self.patternProperties = patternProperties
        self.dependencies = dependencies

    @classmethod
    def fromJson(cls, instance, referrant=None):
        instance = super().fromJson(instance, referrant=referrant)
        for name, member in instance.properties.items():
            if isinstance(member, (Primitive, Union)):
                continue
            member = Creator.create(member.get('type')).fromJson(
                member, referrant=referrant)
            instance.properties[name] = member.resolve(referrant=referrant)
        return instance

    def __call__(self, instance):
        for name, member in instance.items():
            self.properties[name](member)
        if self.maxProperties:
            assert len(instance.keys()) <= self.maxProperties
        assert len(instance.keys()) >= self.minProperties
        if self.required:
            assert len(set(self.required).difference(set(instance))) == 0
        return super().__call__(instance)


class String(Primitive):
    """A JSON string."""

    keywords = ('maxLength', 'minLength', 'pattern',)

    def __init__(self, maxLength=0, minLength=0, pattern='', **kwargs):
        super().__init__(**kwargs)
        self.maxLength = maxLength
        self.minLength = minLength
        self.pattern = pattern

    def __call__(self, instance):
        import re

        if self.maxLength:
            assert len(instance) <= self.maxLength
        assert len(instance) >= self.minLength
        if self.pattern:
            assert re.match(self.pattern, instance) is not None
        return super().__call__(instance)


class Union:

    def __init__(self, type=None, title='', description='', default=None):
        self.type = type

        # Metadata keywords
        self.title = title
        self.description = description
        self.default = default

    @classmethod
    def fromJson(cls, instance, referrant=None):
        types = instance.get('type', [])
        for i, type in enumerate(types):
            if isinstance(type, Primitive):
                continue
            type = Creator.create(type)
            keywords = {}
            for keyword in instance:
                if keyword in type.keywords:
                    keywords[keyword] = instance[keyword]
            keywords['type'] = type.__name__
            types[i] = type.fromJson(keywords, referrant=referrant)
        return cls(type=types)

    def accept(self, visitor):
        return visitor.visitUnion(self)

    def __call__(self, instance):
        cls = EntityMapperTranslator.translate(instance)
        index = [type.__class__ for type in self.type].index(cls)
        return self.type[index](instance)


class Reference:

    def __init__(self, **kwargs):
        self.value = kwargs.get('$ref', '')

    @classmethod
    def fromJson(cls, instance, referrant=None):
        return cls(**instance)
