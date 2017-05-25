import json
import os
import unittest

from aptos.models import OpenAPI, TypeVisitor
from aptos.visitors import RecordVisitor


class OpenAPITestCase(unittest.TestCase):

    def runTest(self):
        with open(os.path.join(os.path.dirname(__file__), 'schemas', 'swagger')) as fp:  # noqa: E501
            instance = json.load(fp)
        specification = OpenAPI.fromJson(instance)
        specification.accept(TypeVisitor(instance))
