<p align="center">
  <br>
  <br>
  <a href="https://github.com/pennsignals/aptos"><img src="https://rawgit.com/rightlag/4042a246cf8639e56c69e0b62de9cb11/raw/fc71de19c792ec9596f0343962f31a4a8309a46f/aptos.svg" alt="aptos"></a>
  <br>
  <br>
</p>

<p align="center">
  <a href="https://travis-ci.org/pennsignals/aptos"><img src="https://img.shields.io/travis/pennsignals/aptos.svg?style=flat-square"></a>
  <a href="https://coveralls.io/github/pennsignals/aptos"><img src="https://img.shields.io/coveralls/pennsignals/aptos.svg?style=flat-square"></a>
</p>

---

`aptos` ([Avro](https://avro.apache.org/), [Protobuf](https://developers.google.com/protocol-buffers/), [Thrift](https://thrift.apache.org/) on [Swagger](http://swagger.io/)) is a module that parses [JSON Schema](http://json-schema.org/) documents to validate client-submitted data and convert JSON schema documents to Avro, Protobuf, or Thrift serialization formats.

JSON Schema defines the media type `"application/schema+json"`, a JSON-based format for describing the structure of JSON data.

<p align="center">
  <img src="https://user-images.githubusercontent.com/2184329/27149976-7a61fa2c-5113-11e7-91be-ef829f4479aa.gif" width="800">
</p>

# Usage

`aptos` supports validating client-submitted data and generating Avro, Protobuf, and Thrift structured messages from a given JSON Schema document.

## Data Validation

Given a JSON Schema document, `aptos` can validate client-submitted data to require that it satisfies a certain number of criteria.

```json
{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Product",
    "type": "object",
    "definitions": {
        "geo": {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "description": "A geographical coordinate",
            "type": "object",
            "properties": {
                "latitude": { "type": "number" },
                "longitude": { "type": "number" }
            }
        }
    },
    "properties": {
        "id": {
            "description": "The unique identifier for a product",
            "type": "number"
        },
        "name": {
            "type": "string"
        },
        "price": {
            "type": "number",
            "minimum": 0,
            "exclusiveMinimum": true
        },
        "tags": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "minItems": 1,
            "uniqueItems": true
        },
        "dimensions": {
            "type": "object",
            "properties": {
                "length": {"type": "number"},
                "width": {"type": "number"},
                "height": {"type": "number"}
            },
            "required": ["length", "width", "height"]
        },
        "warehouseLocation": {
            "description": "Coordinates of the warehouse with the product",
            "$ref": "#/definitions/geo"
        }
    },
    "required": ["id", "name", "price"]
}
```

Validation keywords such as `uniqueItems`, `required`, and `minItems` can be used in a schema to impose requirements for successful validation of an instance.

```python
import json

from aptos.util import Parser
from aptos.visitors import ValidationVisitor

record = Parser.parse('/path/to/schema')
# Valid client-submitted data (instance)
instance = {
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
record.accept(ValidationVisitor(instance))
```

## Structured Message Generation

Given a JSON Schema document, `aptos` can generate structured messages including Avro, Protobuf, and Thrift.

### Avro

For brevity, the [Product](https://github.com/pennsignals/aptos/blob/master/tests/schemas/product) schema is omitted from the example.

```python
import json

from aptos.util import Parser
from aptos.visitors import RecordVisitor

record = Parser.parse('/path/to/schema')
schema = record.accept(RecordVisitor())
print(json.dumps(schema, indent=2))
```

The preceding code generates the following Avro schema:

```json
{
  "namespace": "aptos.visitors",
  "fields": [
    {
      "type": "long",
      "doc": "The unique identifier for a product",
      "name": "id"
    },
    {
      "type": {
        "items": "string",
        "type": "array"
      },
      "doc": "",
      "name": "tags"
    },
    {
      "type": {
        "namespace": "aptos.visitors",
        "fields": [
          {
            "type": "long",
            "doc": "",
            "name": "latitude"
          },
          {
            "type": "long",
            "doc": "",
            "name": "longitude"
          }
        ],
        "type": "record",
        "doc": "A geographical coordinate",
        "name": ""
      },
      "doc": "A geographical coordinate",
      "name": "warehouseLocation"
    },
    {
      "type": "string",
      "doc": "",
      "name": "name"
    },
    {
      "type": {
        "namespace": "aptos.visitors",
        "fields": [
          {
            "type": "long",
            "doc": "",
            "name": "width"
          },
          {
            "type": "long",
            "doc": "",
            "name": "height"
          },
          {
            "type": "long",
            "doc": "",
            "name": "length"
          }
        ],
        "type": "record",
        "doc": "",
        "name": ""
      },
      "doc": "",
      "name": "dimensions"
    },
    {
      "type": "long",
      "doc": "",
      "name": "price"
    }
  ],
  "type": "record",
  "doc": "",
  "name": "Product"
}
```
