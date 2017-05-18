import json
import os
import unittest

from aptos.util import Parser
from aptos.visitors import RecordVisitor


class VisitorTestCase(unittest.TestCase):

    def runTest(self):
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
        record(instance)
        schema = record.accept(RecordVisitor())
        self.assertEqual(len(schema['fields']), 6)
        print(json.dumps(schema, indent=2))
