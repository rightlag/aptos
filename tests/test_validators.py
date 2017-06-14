import unittest

from aptos import primitives
from aptos.visitors import ValidationVisitor


class StringValidatorTestCase(unittest.TestCase):

    def runTest(self):
        component = primitives.String(minLength=2, maxLength=3)
        with self.assertRaises(AssertionError):
            component.accept(ValidationVisitor('A'))
        with self.assertRaises(AssertionError):
            component.accept(ValidationVisitor('ABCD'))
        component = primitives.String(pattern=r'^(\\([0-9]{3}\\))?[0-9]{3}-[0-9]{4}$')  # noqa
        with self.assertRaises(AssertionError):
            component.accept(ValidationVisitor('(888)555-1212 ext. 532'))


class ObjectValidatorTestCase(unittest.TestCase):

    def runTest(self):
        component = primitives.Record(
            properties=primitives.Properties({
                'name': primitives.String(),
                'email': primitives.String(),
                'address': primitives.String(),
                'telephone': primitives.String(),
            }),
            required=['name', 'email']
        )
        with self.assertRaises(AssertionError):
            component.accept(ValidationVisitor({
                'name': 'William Shakespeare',
                'address': 'Henley Street, Stratford-upon-Avon, Warwickshire, England',  # noqa
            }))
        component = primitives.Record(minProperties=2, maxProperties=3)
        with self.assertRaises(AssertionError):
            component.accept(ValidationVisitor({}))
        with self.assertRaises(AssertionError):
            component.accept(ValidationVisitor({'a': 0}))
        with self.assertRaises(AssertionError):
            component.accept(ValidationVisitor(
                {'a': 0, 'b': 1, 'c': 2, 'd': 3}))


class ArrayValidatorTestCase(unittest.TestCase):

    def runTest(self):
        component = primitives.Array(items=primitives.String())
        component = primitives.Array(items=[
            primitives.Integer(),
            primitives.String(),
            primitives.String(enum=['Street', 'Avenue', 'Boulevard']),
            primitives.String(enum=['NW', 'NE', 'SW', 'SE']),
        ])
        with self.assertRaises(AssertionError):
            component.accept(ValidationVisitor([24, 'Sussex', 'Drive']))
        component = primitives.Array(
            items=primitives.Integer(), minItems=2, maxItems=3)
        with self.assertRaises(AssertionError):
            component.accept(ValidationVisitor([]))
        with self.assertRaises(AssertionError):
            component.accept(ValidationVisitor([1, 2, 3, 4]))
        component = primitives.Array(
            items=primitives.Integer(), uniqueItems=True)
        with self.assertRaises(AssertionError):
            component.accept(ValidationVisitor([1, 2, 3, 3, 4]))
