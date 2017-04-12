[![Travis](https://img.shields.io/travis/pennsignals/aptos.svg?style=flat-square)](https://travis-ci.org/pennsignals/aptos)

```python
import json

from aptos.util import read
from aptos.visitors import AvroSerializer

specification = read(open('/path/to/schema'))
print(json.dumps(specification.definitions['Pet'].accept(AvroSerializer()), indent=2))
```

```json
{
  "type": "record",
  "fields": [
    {
      "type": "array",
      "items": "string",
      "name": "photoUrls"
    },
    {
      "type": "string",
      "name": "name"
    },
    {
      "type": "array",
      "items": {
        "type": "record",
        "fields": [
          {
            "type": "string",
            "name": "name"
          },
          {
            "type": "long",
            "name": "id"
          }
        ]
      },
      "name": "tags"
    },
    {
      "type": "long",
      "name": "id"
    },
    {
      "type": {
        "type": "record",
        "fields": [
          {
            "type": "string",
            "name": "name"
          },
          {
            "type": "long",
            "name": "id"
          }
        ]
      },
      "name": "category"
    },
    {
      "type": "string",
      "name": "status"
    }
  ]
}
```
