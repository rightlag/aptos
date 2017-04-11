import os
import unittest

from aptos.util import read
from aptos.primitives import Array, Reference, Object


class LoaderTestCase(unittest.TestCase):

    def runTest(self):
        specification = read(open(
            os.path.join(os.path.dirname(__file__), 'schemas', 'petstore.json')))
        self.assertEqual(len(specification.definitions), 6)
        definitions = ['Order', 'Category', 'User', 'Tag', 'Pet',
                       'ApiResponse']
        for definition in definitions:
            self.assertIn(definition, specification.definitions)
        Pet = specification.definitions['Pet']
        self.assertIsInstance(Pet.properties['category'], Reference)
        self.assertIsInstance(Pet.properties['tags'], Array)
        self.assertIsInstance(Pet.properties['tags'].items.value, Object)
        with self.assertRaises(AssertionError):
            Pet(dict())  # 'name' and 'photoUrls' required
