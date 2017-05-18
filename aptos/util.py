import json

from .primitives import Record
from .visitors import ResolveVisitor


class Parser:

    @staticmethod
    def parse(filename):
        with open(filename) as fp:
            instance = json.load(fp)
        record = Record.fromJson(instance)
        record.accept(ResolveVisitor(instance))
        return record
