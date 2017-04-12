import json
import os
import unittest

from aptos.util import read
from aptos.visitors import AvroSerializer


class VisitorTestCase(unittest.TestCase):

    def runTest(self):
        specification = read(open(
            os.path.join(os.path.dirname(__file__), 'schemas',
                         'petstore.json')))
        v = specification.definitions['Pet'].accept(AvroSerializer())
        print(json.dumps(v, indent=2))
