import re


class TypeFactory:

    @staticmethod
    def construct_type(type, format):
        return {
            ('array', ''): Array,
            ('boolean', ''): Boolean,
            ('integer', 'int32'): Integer,
            ('integer', 'int64'): Long,
            ('number', ''): Number,
            ('object', ''): Object,
            ('string', ''): String,
            ('string', 'date-time'): String,  # TODO: fix dateTime type
            (None, ''): Reference,  # TODO: try/except instead?
        }[type, format]


class Primitive:

    def __init__(self, enum=None, type='', allOf=None, title='',
                 description='', default=None, discriminator='',
                 readOnly=False, xml=None, externalDocs=None, example=None,
                 format=''):
        self.enum = [] if enum is None else list(enum)
        self.type = type
        self.allOf = allOf
        self.title = title
        self.description = description
        self.default = default
        self.discriminator = discriminator
        self.readOnly = readOnly
        self.xml = xml
        self.externalDocs = externalDocs
        self.example = example
        self.format = format

    def resolve(self, referrant=None):
        return self

    @classmethod
    def load(cls, instance):
        return cls(**instance)

    def __call__(self, instance):
        raise NotImplementedError()  # validation


class Array(Primitive):

    def __init__(self, items=None, maxItems=0, minItems=0, uniqueItems=False,
                 **kwargs):
        super().__init__(**kwargs)
        self.items = items  # object MUST be a valid JSON Schema
        self.maxItems = maxItems
        self.minItems = minItems
        self.uniqueItems = uniqueItems

    @classmethod
    def load(cls, instance):
        items = instance.get('items', {})
        items = TypeFactory.construct_type(
            items.get('type'), items.get('format', '')).load(items)
        instance['items'] = items
        return super().load(instance)

    def resolve(self, referrant):
        self.items = self.items.resolve(referrant)
        return self

    def __call__(self, instance):
        for child in instance:
            self.items(child)  # validate children instances
        if self.maxItems:
            assert len(instance) <= self.maxItems
        assert len(instance) >= self.minItems
        if self.uniqueItems:
            assert len(list(set(instance))) == len(instance)
        return self


class Boolean(Primitive):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Integer(Primitive):

    def __init__(self, multipleOf=0, maximum=0, exclusiveMaximum=False,
                 minimum=0, exclusiveMinimum=False, **kwargs):
        super().__init__(**kwargs)
        self.multipleOf = multipleOf
        self.maximum = maximum
        self.exclusiveMaximum = exclusiveMaximum
        self.minimum = minimum
        self.exclusiveMinimum = exclusiveMinimum

    def __call__(self, instance):
        # TODO: implement validation logic
        return self


class Long(Integer):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Number(Primitive):

    def __init__(self, multipleOf=0, maximum=0, exclusiveMaximum=False,
                 minimum=0, exclusiveMinimum=False, **kwargs):
        super().__init__(**kwargs)
        self.multipleOf = multipleOf
        self.maximum = maximum
        self.exclusiveMaximum = exclusiveMaximum
        self.minimum = minimum
        self.exclusiveMinimum = exclusiveMinimum

    def __call__(self, instance):
        # TODO: implement validation logic
        return self


class Null(Primitive):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self, instance):
        # TODO: implement validation logic
        return self


class Object(Primitive):

    def __init__(self, maxProperties=0, minProperties=0, required=None,
                 additionalProperties=None, properties=None, **kwargs):
        super().__init__(**kwargs)
        self.maxProperties = maxProperties
        self.minProperties = minProperties
        self.required = [] if required is None else list(set(required))
        self.additionalProperties = additionalProperties
        self.properties = properties

    @classmethod
    def load(cls, instance, referrant=None):
        # TODO: should referrant be None?
        for name, member in instance.get('properties', {}).items():
            if isinstance(member, Primitive):
                continue  # already of primitive type
            member = TypeFactory.construct_type(
                member.get('type'), member.get('format', '')).load(member)
            instance['properties'][name] = member.resolve(referrant)
        return super().load(instance)

    def __call__(self, instance):
        if self.maxProperties:
            assert len(instance.keys()) <= self.maxProperties
        assert len(instance.keys()) >= self.minProperties
        if self.required:
            # TODO: compare against values in properties?
            required = list(self.required)  # shallow copy required list
            for name in instance.keys():
                if name in required:
                    required.remove(name)
            assert len(required) == 0
        return self


class String(Primitive):

    def __init__(self, maxLength=0, minLength=0, pattern='', **kwargs):
        super().__init__(**kwargs)
        self.maxLength = maxLength
        self.minLength = minLength
        self.pattern = pattern

    def __call__(self, instance):
        if self.maxLength:
            assert len(instance) <= self.maxLength
        assert len(instance) >= self.minLength
        if self.pattern:
            assert re.match(self.pattern, instance) is not None
        return self


class Reference:

    def __init__(self, **kwargs):
        self.value = kwargs.get('$ref', '')

    def resolve(self, referrant):
        value = referrant['definitions'][self.value.split('/')[-1]]
        if not isinstance(value, Object):
            value = Object.load(value, referrant=referrant)
        self.value = value
        return self

    @classmethod
    def load(cls, instance):
        return cls(**instance)

    def __call__(self, instance):
        return self.value(instance)
