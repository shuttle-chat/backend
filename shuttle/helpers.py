# Copyright 2023 iiPython

# Modules
import json
from blacksheep import Response, Content

# resp_json
def resp_json(data: dict) -> Response:
    return Response(
        status = data.get("code", 200),  # You should really have code specified
        content = Content(b"application/json", json.dumps(data).encode("utf8"))
    )
