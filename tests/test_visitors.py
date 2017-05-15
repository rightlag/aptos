import json
import os
import unittest

from aptos.util import Parser
from aptos.visitors import RecordVisitor


class VisitorTestCase(unittest.TestCase):

    def runTest(self):
        specification = Parser.parse(
            os.path.join(os.path.dirname(__file__), 'schemas', 'product'))
        record = specification.accept(RecordVisitor())
        self.assertEqual(len(record['fields']), 6)
        print(json.dumps(record, indent=2))
