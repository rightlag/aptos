import os
import unittest

from aptos.primitives import String, Array
from aptos.util import read


class ValidatorTestCase(unittest.TestCase):

    def runTest(self):
        specification = read(open(os.path.join(
            os.path.dirname(__file__), 'schemas', 'petstore.json')))

        with self.assertRaises(AssertionError):
            # 'name' and 'photoUrls' required
            specification.definitions['Pet'](dict())

        s = String(maxLength=5)
        with self.assertRaises(AssertionError):
            s('hello, world!')  # fails validation

        arr = Array(items=String(), maxItems=3)  # array of type 'String'
        with self.assertRaises(AssertionError):
            arr(['a', 'b', 'c', 'd'])

        # further validation of children items
        arr = Array(items=String(maxLength=1))
        with self.assertRaises(AssertionError):
            arr(['ab'])

        arr = Array(items=String(), uniqueItems=True)
        with self.assertRaises(AssertionError):
            arr(['d', 'e', 'g', 'g'])  # duplicate items in array
