<p align="center">
  <img src="assets/title.png">
</p>

<p align="center">
  <a href="https://travis-ci.org/pennsignals/aptos"><img src="https://img.shields.io/travis/pennsignals/aptos.svg?style=flat-square"></a>
  <a href="https://coveralls.io/github/pennsignals/aptos"><img src="https://img.shields.io/coveralls/pennsignals/aptos.svg?style=flat-square"></a>
</p>

```python
import json

from aptos.util import parse
from aptos.visitors import RecordVisitor

specification = parse(open('/path/to/schema'))
print(json.dumps(specification.definitions['Pet'].accept(RecordVisitor()), indent=2))
```

```json
{
  "type": "record",
  "name": "Pet",
  "namespace": "aptos.visitors",
  "doc": "",
  "fields": [
    {
      "type": "string",
      "name": "name",
      "doc": ""
    },
    {
      "type": {
        "type": "record",
        "name": "Category",
        "namespace": "aptos.visitors",
        "doc": "",
        "fields": [
          {
            "type": "string",
            "name": "name",
            "doc": ""
          },
          {
            "type": "int",
            "name": "id",
            "doc": ""
          }
        ]
      },
      "name": "category",
      "doc": ""
    },
    {
      "type": "string",
      "name": "status",
      "doc": "pet status in the store"
    },
    {
      "type": "int",
      "name": "id",
      "doc": ""
    },
    {
      "type": {
        "type": "array",
        "items": "string"
      },
      "name": "photoUrls",
      "doc": ""
    },
    {
      "type": {
        "type": "array",
        "items": {
          "type": "record",
          "name": "Tag",
          "namespace": "aptos.visitors",
          "doc": "",
          "fields": [
            {
              "type": "string",
              "name": "name",
              "doc": ""
            },
            {
              "type": "int",
              "name": "id",
              "doc": ""
            }
          ]
        }
      },
      "name": "tags",
      "doc": ""
    }
  ]
}

```
