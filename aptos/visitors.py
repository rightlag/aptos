import re

from . import primitives


class Visitor:

    def visitPrimitive(self, primitive, *args):
        if isinstance(primitive, primitives.Reference):
            return primitive
        primitive.allOf.accept(self, *args)
        primitive.definitions.accept(self, *args)
        return primitive

    def visitDefinitions(self, definitions, *args):
        for name, member in definitions.items():
            member = self.visitPrimitive(member, *args)
            definitions[name] = member.accept(self, *args)

    def visitProperties(self, properties, *args):
        for name, member in properties.items():
            member = self.visitPrimitive(member, *args)
            properties[name] = member.accept(self, *args)

    def visitAllOf(self, allOf, *args):
        for i, item in enumerate(allOf):
            item = self.visitPrimitive(item, *args)
            allOf[i] = item.accept(self, *args)

    def visitUnion(self, union, *args):
        return self.visitPrimitive(union, *args)

    def visitArray(self, array, *args):
        array = self.visitPrimitive(array, *args)
        array.items = array.items.accept(self, *args)
        return array

    def visitInt(self, integer, *args):
        return self.visitPrimitive(integer, *args)

    def visitLong(self, long, *args):
        return self.visitPrimitive(long, *args)

    def visitString(self, string, *args):
        return self.visitPrimitive(string, *args)

    def visitEnum(self, enumeration, *args):
        return self.visitPrimitive(enumeration, *args)

    def visitDeclared(self, declared, *args):
        declared = self.visitPrimitive(declared, *args)
        declared.properties.accept(self, *args)
        return declared


class RecordVisitor(Visitor):

    def visitEnum(self, enumeration, *args):
        return {
            'type': 'enum', 'name': enumeration.title,
            'doc': enumeration.description, 'symbols': enumeration.enum}

    def visitUnion(self, union, *args):
        return {'type': list(
            identifier.accept(self)['type'] for identifier in union.type)}

    def visitArray(self, array, *args):
        items = array.items.accept(self)
        if 'fields' not in items:
            items = items['type']
        return {'type': 'array', 'items': items}

    def visitBoolean(self, boolean, *args):
        return {'type': 'boolean'}

    def visitInt(self, integer, *args):
        return {'type': 'int'}

    def visitLong(self, long, *args):
        return {'type': 'long'}

    def visitFloat(self, float, *args):
        return {'type': 'float'}

    def visitNull(self, null, *args):
        return {'type': 'null'}

    def visitDeclared(self, declared, *args):
        fields = []
        for name, member in declared.properties.items():
            field = member.accept(self)
            if isinstance(member, (primitives.Record, primitives.Array)):
                field = {'type': field}
            field.update({'name': name, 'doc': member.description})
            fields.append(field)
        for item in declared.allOf:
            # Index `fields` if `item` is of type `Record`.
            fields.extend(
                item.accept(self).get('fields', [item.accept(self, *args)]))
        return {
            'type': 'record', 'namespace': __name__, 'name': declared.title,
            'doc': declared.description, 'fields': fields}

    def visitString(self, string):
        return {'type': 'string'}


class TypeVisitor(Visitor):

    def __init__(self, context):
        self.context = context

    def visitUnknown(self, unknown, *args):
        value = unknown.value.split('/')[-1]
        instance = self.context['definitions'][value]
        return primitives.Creator.create(
            instance.get('type')).fromJson(instance)


class ValidationVisitor(Visitor):

    def __init__(self, instance):
        self.instance = instance

    def visitPrimitive(self, primitive, *args):
        instance = self.instance
        for element in primitive.enum:
            assert instance in primitive.enum
        primitive.allOf.accept(self, *args)
        return primitive

    def visitEnum(self, enumeration, *args):
        instance = self.instance
        enumeration = self.visitPrimitive(enumeration, *args)
        if enumeration.enum:
            assert instance in enumeration.enum, (
                '%r not equal to one of the elements in this keyword\'s array value %r' % (instance, enumeration.enum))  # noqa: E501

    def visitArray(self, array, *args):
        instance = self.instance
        array = self.visitPrimitive(array, *args)
        if isinstance(array.items, primitives.Component):
            for element in instance:
                array.items.accept(ValidationVisitor(element))
        else:
            for i, element in enumerate(instance):
                array.items[i].accept(ValidationVisitor(element))
        if not array.additionalItems and isinstance(
                array.items, primitives.Array):
            assert len(instance) <= array.items
        if array.maxItems:
            assert len(instance) <= array.maxItems, (
                '%r is not less than, or equal to, the value of this keyword %r' % (len(instance), array.maxItems))  # noqa: E501
        assert len(instance) >= array.minItems, (
            '%r is not greater than, or equal to, the value of this keyword %r' % (len(instance), array.minItems))  # noqa: E501
        if array.uniqueItems:
            assert len(list(set(instance))) == len(instance), (
                '%r elements are not unique %r' % (instance, array.uniqueItems))  # noqa: E501

    def visitString(self, string, *args):
        instance = self.instance
        string = self.visitPrimitive(string, *args)
        if string.maxLength:
            assert len(instance) <= string.maxLength, (
                '%r is not less than, or equal to, the value of this keyword %r' % (len(instance), string.maxLength))  # noqa: E501
        assert len(instance) >= string.minLength, (
            '%r is not greater than, or equal to, the value of this keyword %r' % (len(instance), string.minLength))  # noqa: E501
        if string.pattern:
            assert re.match(string.pattern, instance) is not None, (
                '%r does not match the instance successfully %r' % (string.pattern, instance))  # noqa: E501

    def visitInt(self, integer, *args):
        # TODO: write `visitInt` functionality.
        pass

    def visitLong(self, long, *args):
        # TODO: write `visitLong` functionality.
        pass

    def visitAllOf(self, allOf, *args):
        for item in allOf:
            item.accept(self, *args)

    def visitNull(self, null, *args):
        self.visitPrimitive(null, *args)

    def visitUnion(self, union, *args):
        union = self.visitPrimitive(union, *args)
        instance = args[0]
        cls = primitives.Translator.translate(instance)
        index = [type.__class__ for type in union.type].index(cls)
        union.type[index].accept(self, *args)

    def visitDeclared(self, declared, *args):
        instance = self.instance
        declared = self.visitPrimitive(declared, *args)
        if declared.maxProperties:
            assert len(instance.keys()) <= declared.maxProperties, (
                '%r is not less than, or equal to, the value of this keyword %r' % (len(instance.keys()), declared.maxProperties))  # noqa: E501
        assert len(instance.keys()) >= declared.minProperties, (
            '%r is not greater than, or equal to, the value of this keyword %r' % (len(instance.keys()), declared.minProperties))  # noqa: E501
        for item in declared.required:
            assert item in instance, '%r is not the name of a property in the instance %r' % (declared.required, item)  # noqa: E501
        declared.properties.accept(self)

    def visitProperties(self, properties, *args):
        for name, member in self.instance.items():
            if properties.get(name) is None:
                continue
            properties[name].accept(ValidationVisitor(member))
