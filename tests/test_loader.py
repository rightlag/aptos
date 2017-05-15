import os
import unittest

from aptos.util import Parser
from aptos.primitives import Array, Record


class LoaderTestCase(unittest.TestCase):

    def runTest(self):
        record = Parser.parse(os.path.join(
            os.path.dirname(__file__), 'schemas', 'product'))

        self.assertEqual(len(record.definitions), 1)
        self.assertIsInstance(record.properties['warehouseLocation'], Record)
        self.assertIsInstance(record.properties['tags'], Array)
