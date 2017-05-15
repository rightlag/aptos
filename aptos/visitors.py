from . import primitives


class RecordVisitor:

    def visitEnum(self, enumeration):
        return {'type': {
            'type': 'enum', 'name': enumeration.title,
            'doc': enumeration.description, 'symbols': enumeration.enum}}

    def visitUnion(self, union):
        return {'type': list(
            identifier.accept(self)['type'] for identifier in union.type)}

    def visitArray(self, array):
        items = array.items.accept(self)
        if 'fields' not in items:
            items = items['type']
        return {'type': 'array', 'items': items}

    def visitBoolean(self, boolean):
        return {'type': 'boolean'}

    def visitInt(self, integer):
        return {'type': 'int'}

    def visitLong(self, long):
        return {'type': 'long'}

    def visitFloat(self, float):
        return {'type': 'float'}

    def visitNull(self, null):
        return {'type': 'null'}

    def visitDeclared(self, declared):
        fields = []
        for name, member in declared.properties.items():
            field = member.accept(self)
            if isinstance(member, (primitives.Object, primitives.Array)):
                field = {'type': field}
            field.update({'name': name, 'doc': member.description})
            fields.append(field)
        for item in declared.allOf.items:
            fields.extend(item.accept(self)['fields'])
        return {
            'type': 'record', 'namespace': __name__, 'name': declared.title,
            'doc': declared.description, 'fields': fields}

    def visitString(self, string):
        return {'type': 'string'}


class Visitor:

    def visit(self, primitive):
        primitive = primitive.accept(self)
        for i, item in enumerate(primitive.allOf.items):
            primitive.allOf.items[i] = item.accept(self)
        return primitive


class ResolveVisitor(Visitor):

    def __init__(self, context):
        self.context = context

    def visitUnion(self, union):
        return union

    def visitArray(self, array):
        array.items = array.items.accept(self)
        return array

    def visitInt(self, integer):
        return integer

    def visitString(self, string):
        return string

    def visitUnknown(self, unknown):
        value = unknown.value.split('/')[-1]
        instance = self.context['definitions'][value]
        return Creator.create(instance.get('type')).fromJson(instance)

    def visitDeclared(self, declared):
        for i, item in enumerate(declared.allOf.items):
            declared.allOf.items[i] = super().visit(item)
        declared.properties.accept(self)
        declared.definitions.accept(self)
        return declared
