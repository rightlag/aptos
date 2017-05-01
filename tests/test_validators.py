import json
import unittest

from aptos import primitives
from aptos.visitors import RecordVisitor


class ValidatorTestCase(unittest.TestCase):

    def runTest(self):
        product = primitives.Object(
            title='Product',
            description='A product from Acme\'s catalog',
            type='object',
            properties={
                'id': primitives.Integer(
                    description='The unique identifier for a product',
                    type='integer'),
                'name': primitives.String(
                    description='Name of the product', type='string'),
                'price': primitives.Number(
                    type='number', minimum=0, exclusiveMinimum=True),
                'tags': primitives.Array(
                    type='array', items=primitives.String(type='string'),
                    minItems=1, uniqueItems=True),
            },
            required=['id', 'name', 'price']
        )

        instance = {
            "id": 1,
            "name": "A green door",
            "price": 12.50,
            "tags": ["home", "green"]
        }

        product(instance)
        record = product.accept(RecordVisitor())
        print(json.dumps(record, indent=2))
