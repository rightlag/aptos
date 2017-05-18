import json
import os
import unittest

from aptos.util import Parser
from aptos.primitives import Array, Record
from aptos.visitors import ValidationVisitor


class LoaderTestCase(unittest.TestCase):

    def runTest(self):
        record = Parser.parse(os.path.join(
            os.path.dirname(__file__), 'schemas', 'product'))
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
        self.assertEqual(len(record.definitions), 1)
        self.assertIsInstance(record.properties['warehouseLocation'], Record)
        self.assertIsInstance(record.properties['tags'], Array)
