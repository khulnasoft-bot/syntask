import json

from syntask.server.api.server import create_app

app = create_app()
openapi_schema = app.openapi()

with open("oss_schema.json", "w") as f:
    json.dump(openapi_schema, f)
