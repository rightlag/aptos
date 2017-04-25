class TypeVisitor:

    def visitUnion(self, union):
        children = union.type
        for i, child in enumerate(children):
            children[i] = child.accept(self)['type']
        return {'type': children}

    def visitArray(self, array):
        items = array.items.accept(self)
        if 'fields' not in items:
            items = items.get('type')
        return {'type': {'type': 'array', 'items': items}}

    def visitBoolean(self, boolean):
        return {'type': 'boolean'}

    def visitInt(self, integer):
        return {'type': 'int'}

    def visitLong(self, long):
        return {'type': 'long'}

    def visitNull(self, null):
        return {'type': 'null'}

    def visitDeclared(self, declared):
        fields = []
        for name, member in declared.properties.items():
            field = member.accept(self)
            field.update({'name': name, 'doc': member.description})
            fields.append(field)
        return {'type': {
            'type': 'record', 'namespace': __name__, 'name': declared.title,
            'doc': declared.description, 'fields': fields}}

    def visitString(self, string):
        return {'type': 'string'}
