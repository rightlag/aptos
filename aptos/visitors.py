class TypeVisitor:

    def visit(self, v):
        raise NotImplementedError()

    def visit_type(self, properties):
        raise NotImplementedError()

    def visit_array(self, items):
        raise NotImplementedError()

    def visit_boolean(self, b):
        raise NotImplementedError()

    def visit_int(self, i):
        raise NotImplementedError()

    def visit_long(self, i):
        raise NotImplementedError()

    def visit_string(self, s):
        raise NotImplementedError()


class AvroSerializer(TypeVisitor):

    def visit(self, v):
        return {'type': v.accept(self)}

    def visit_type(self, properties):
        fields = []
        for name, member in properties.items():
            field = member.accept(self)
            field['name'] = name
            fields.append(field)
        return {'type': 'record', 'fields': fields}

    def visit_array(self, items):
        items = items.accept(self)
        if 'fields' not in items:
            items = items.get('type')
        return {'type': 'array', 'items': items}

    def visit_boolean(self, b):
        return {'type': 'boolean'}

    def visit_int(self, i):
        return {'type': 'int'}

    def visit_long(self, i):
        return {'type': 'long'}

    def visit_string(self, s):
        return {'type': 'string'}
