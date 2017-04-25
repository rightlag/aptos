import json
import os
import unittest

from aptos.util import parse
from aptos.visitors import TypeVisitor


class VisitorTestCase(unittest.TestCase):

    def runTest(self):
        specification = parse(open(
            os.path.join(os.path.dirname(__file__), 'schemas',
                         'petstore.json')))
        Pet = specification.definitions['Pet'].accept(TypeVisitor())['type']
        self.assertEqual(len(Pet['fields']), 6)
        print(json.dumps(Pet, indent=2))
