<p align="center">
  <img src="assets/title.png">
</p>

<p align="center">
  <a href="https://travis-ci.org/pennsignals/aptos"><img src="https://img.shields.io/travis/pennsignals/aptos.svg?style=flat-square"></a>
  <a href="https://coveralls.io/github/pennsignals/aptos"><img src="https://img.shields.io/coveralls/pennsignals/aptos.svg?style=flat-square"></a>
</p>

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
