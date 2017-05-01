class JSONSchema:

    types = (
        'array', 'boolean', 'integer', 'number', 'null', 'object', 'string',)


class EntityMapperTranslator:

    def __call__(self, instance):
        return {
            dict: Object,
            list: Array,
            tuple: Array,
            str: String,
            int: Integer,
            float: Number,
            bool: Boolean,
            type(None): Null,
        }[instance.__class__]


class TypeRegistry:

    @staticmethod
    def find(type):
        if isinstance(type, list):
            return Union

        return {
            'object': Object,
            'array': Array,
            'string': String,
            'integer': Integer,
            'number': Number,
            'boolean': Boolean,
            'null': Null,
            None: Reference,
        }[type]


class Primitive:

    keywords = ('enum', 'type', 'allOf', 'anyOf', 'oneOf', 'definitions',)

    def __init__(self, enum=None, type=None, allOf=None, anyOf=None,
                 oneOf=None, definitions=None, title='', description='',
                 default=None, **kwargs):
        # TODO: include `not`
        self.enum = [] if enum is None else list(set(enum))
        children = [type] if isinstance(type, str) else list(set(type))
        assert all([child.lower() in JSONSchema.types for child in children]), (  # noqa: E501
            'got an unexpected keyword argument %r' % children.pop())
        self.type = children if len(children) > 1 else children.pop()
        self.allOf = [] if allOf is None else list(allOf)
        self.anyOf = [] if anyOf is None else list(anyOf)
        self.oneOf = [] if oneOf is None else list(oneOf)
        self.definitions = {} if definitions is None else dict(definitions)

        # Metadata keywords
        self.title = title
        self.description = description
        self.default = default

    @classmethod
    def fromJson(cls, instance, referrant=None):
        if 'allOf' in instance:
            properties = {}
            for schema in instance.get('allOf', []):
                schema = TypeRegistry.find(schema.get('type')).fromJson(
                    schema, referrant=referrant)
                schema = schema.resolve(referrant=referrant)
                properties.update(schema.properties)
            instance['properties'] = properties
        return cls(**instance)

    def resolve(self, referrant=None):
        return self

    def accept(self, visitor):
        return {
            Array: visitor.visitArray,
            Boolean: visitor.visitBoolean,
            Integer: visitor.visitInt,
            Number: visitor.visitLong,
            Null: visitor.visitNull,
            Object: visitor.visitDeclared,
            String: visitor.visitString,
        }[self.__class__](self)

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
        instance.items = TypeRegistry.find(items.get('type')).fromJson(
            items, referrant=referrant)
        return instance

    def resolve(self, referrant=None):
        self.items = self.items.resolve(referrant=referrant)
        return self

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


class Object(Primitive):
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
            member = TypeRegistry.find(member.get('type')).fromJson(
                member, referrant=referrant)
            instance.properties[name] = member.resolve(referrant=referrant)
        return instance

    class Builder:

        @classmethod
        def fromFields(cls, fields):
            return cls

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
            type = TypeRegistry.find(type)
            keywords = {}
            for keyword in instance:
                if keyword in type.keywords:
                    keywords[keyword] = instance[keyword]
            keywords['type'] = type.__name__
            types[i] = type.fromJson(keywords, referrant=referrant)
        return cls(type=types)

    def accept(self, visitor):
        return visitor.visitUnion(self)

    def resolve(self, referrant=None):
        return self

    def __call__(self, instance):
        cls = EntityMapperTranslator()(instance)
        index = [type.__class__ for type in self.type].index(cls)
        return self.type[index](instance)


class Reference:

    def __init__(self, **kwargs):
        self.value = kwargs.get('$ref', '')

    @classmethod
    def fromJson(cls, instance, referrant=None):
        return cls(**instance)

    def resolve(self, referrant=None):
        value = referrant['definitions'][self.value.split('/')[-1]]
        if not isinstance(value, Primitive):
            cls = TypeRegistry.find(value.get('type'))
            value = cls.fromJson(value, referrant=referrant)
        return value
