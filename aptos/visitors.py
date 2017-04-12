class TypeVisitor:
    def visit(self, v):
        raise NotImplementedError()

    def visitType(self, properties):
        raise NotImplementedError()

    def visitArray(self, items):
        raise NotImplementedError()

    def visitBoolean(self, b):
        raise NotImplementedError()

    def visitInt(self, i):
        raise NotImplementedError()

    def visitLong(self, i):
        raise NotImplementedError()

    def visitString(self, s):
        raise NotImplementedError()


class AvroSerializer(TypeVisitor):
    def visit(self, v):
         return {'type': v.accept(self)}

    def visitType(self, properties):
        fields = []
        for name, member in properties.items():
            field = member.accept(self)
            field['name'] = name
            fields.append(field)
        return {'type': 'record', 'fields': fields}

    def visitArray(self, items):
        items = items.accept(self)
        if 'fields' not in items:
            items = items.get('type')
        return {'type': 'array', 'items': items}

    def visitBoolean(self, b):
        return {'type': 'boolean'}

    def visitInt(self, i):
        return {'type': 'int'}

    def visitLong(self, i):
        return {'type': 'long'}

    def visitString(self, s):
        return {'type': 'string'}
