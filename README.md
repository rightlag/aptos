<p align="center">
  <img src="assets/title.png">
</p>

<p align="center">
  <a href="https://travis-ci.org/pennsignals/aptos"><img src="https://img.shields.io/travis/pennsignals/aptos.svg?style=flat-square"></a>
  <a href="https://coveralls.io/github/pennsignals/aptos"><img src="https://img.shields.io/coveralls/pennsignals/aptos.svg?style=flat-square"></a>
</p>

```python
import json

from aptos.util import Parser
from aptos.visitors import RecordVisitor

record = Parser.parse('/path/to/schema')
schema = record.accept(RecordVisitor())
print(json.dumps(schema, indent=2))
```

```json
{
  "doc": "",
  "namespace": "aptos.visitors",
  "name": "Product",
  "fields": [
    {
      "doc": "A geographical coordinate",
      "name": "warehouseLocation",
      "type": {
        "doc": "A geographical coordinate",
        "namespace": "aptos.visitors",
        "name": "",
        "fields": [
          {
            "doc": "",
            "name": "latitude",
            "type": "long"
          },
          {
            "doc": "",
            "name": "longitude",
            "type": "long"
          }
        ],
        "type": "record"
      }
    },
    {
      "doc": "",
      "name": "tags",
      "type": {
        "items": "string",
        "type": "array"
      }
    },
    {
      "doc": "",
      "name": "price",
      "type": "long"
    },
    {
      "doc": "The unique identifier for a product",
      "name": "id",
      "type": "long"
    },
    {
      "doc": "",
      "name": "name",
      "type": [
        "string",
        "null"
      ]
    },
    {
      "doc": "",
      "name": "dimensions",
      "type": {
        "doc": "",
        "namespace": "aptos.visitors",
        "name": "",
        "fields": [
          {
            "doc": "",
            "name": "length",
            "type": "long"
          },
          {
            "doc": "",
            "name": "width",
            "type": "long"
          },
          {
            "doc": "",
            "name": "height",
            "type": "long"
          }
        ],
        "type": "record"
      }
    }
  ],
  "type": "record"
}
```
