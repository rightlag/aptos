import json
import os
import unittest

from aptos.util import Parser
from aptos.visitors import RecordVisitor, ValidationVisitor


class VisitorTestCase(unittest.TestCase):

    def runTest(self):
        records = {}
        record = Parser.parse(
            os.path.join(os.path.dirname(__file__), 'schemas', 'product'))
        instance = json.loads('''
        {
            "id": 2,
            "name": "An ice sculpture",
            "price": 12.50,
            "tags": ["cold", "ice"],
            "dimensions": {
                "length": 7.0,
                "width": 12.0,
                "height": 9.5
            },
            "warehouseLocation": {
                "latitude": -78.75,
                "longitude": 20.4
            }
        }
        ''')
        record.accept(ValidationVisitor(instance))
        schema = record.accept(RecordVisitor())
        self.assertEqual(len(schema['fields']), 6)
        records['Product'] = schema
        record = Parser.parse(
            os.path.join(os.path.dirname(__file__), 'schemas', 'address'))
        instance = json.loads('''
        {
           "street_address": "1600 Pennsylvania Avenue NW",
           "city": "Washington",
           "state": "DC",
           "type": "residential"
        }
        ''')
        record.accept(ValidationVisitor(instance))
        schema = record.accept(RecordVisitor())
        records['Address'] = schema
        print(json.dumps(records, indent=2))
