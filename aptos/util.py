import json

from .primitives import Record
from .visitors import TypeVisitor


class Parser:

    @staticmethod
    def parse(filename):
        with open(filename) as fp:
            instance = json.load(fp)
        record = Record.fromJson(instance)
        record.accept(TypeVisitor(instance))
        return record
