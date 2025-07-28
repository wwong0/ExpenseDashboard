from flask.json.provider import JSONProvider
from pydantic.json import pydantic_encoder
import json

class PydanticJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, default=pydantic_encoder, **kwargs)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)