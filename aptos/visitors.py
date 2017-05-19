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
        for i, item in enumerate(allOf.items):
            item = self.visitPrimitive(item, *args)
            allOf.items[i] = item.accept(self, *args)

    def visitUnion(self, union, *args):
        return self.visitPrimitive(union, *args)

    def visitArray(self, array, *args):
        return self.visitPrimitive(array, *args)

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
        for item in declared.allOf.items:
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
        primitive.allOf.accept(self, *args)
        return primitive

    def visitEnum(self, enumeration, *args):
        enumeration = self.visitPrimitive(enumeration, *args)
        instance = args[0]
        if enumeration.enum:
            assert instance in enumeration.enum

    def visitArray(self, array, *args):
        array = self.visitPrimitive(array, *args)
        instance = args[0]
        if not array.additionalItems and isinstance(
                array.items, primitives.Array):
            assert len(instance) <= array.items
        if array.maxItems:
            assert len(instance) <= array.maxItems
        assert len(instance) >= array.minItems
        if array.uniqueItems:
            assert len(list(set(instance))) == len(instance)

    def visitString(self, string, *args):
        string = self.visitPrimitive(string, *args)
        instance = args[0]
        if string.maxLength:
            assert len(instance) <= string.maxLength
        assert len(instance) >= string.minLength
        if string.pattern:
            assert re.match(string.pattern, instance) is not None

    def visitInt(self, integer, *args):
        # TODO: write `visitInt` functionality.
        pass

    def visitLong(self, long, *args):
        # TODO: write `visitLong` functionality.
        pass

    def visitAllOf(self, allOf, *args):
        for item in allOf.items:
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
        declared = self.visitPrimitive(declared, *args)
        instance = args[0] if args else self.instance
        if declared.maxProperties:
            assert len(instance.keys()) <= declared.maxProperties
        assert len(instance.keys()) >= declared.minProperties
        if declared.required:
            assert len(set(declared.required).difference(set(instance))) == 0
        for name, member in declared.properties.items():
            member.accept(self, instance[name])
