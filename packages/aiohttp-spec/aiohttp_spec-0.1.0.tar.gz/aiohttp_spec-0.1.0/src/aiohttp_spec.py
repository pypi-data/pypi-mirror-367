from functools import wraps

import jsonschema
from aiohttp import web

REQUEST_BODY_SCHEMA = {
    "type": "object",
    "properties": {
        "required": {"type": "boolean"},
        "content": {
            "type": "object",
            "minProperties": 1,
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "schema": {"type": "object"},
                    "examples": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "summary": {"type": "string"},
                                "description": {"type": "string"},
                                "value": {},
                            },
                            "required": ["value"],
                        },
                    },
                    "example": {},
                },
            },
        },
    },
    "required": ["content"],
}

RESPONSES_SCHEMA = {
    "type": "object",
    "additionalProperties": {
        "type": "object",
        "properties": {
            "description": {"type": "string"},
            "content": {"type": "object"},
        },
        "required": ["description"],
    },
}


def spec(summary=None, description=None, tags=None, responses=None, request_body=None):
    def decorator(handler):
        if request_body:
            try:
                jsonschema.validate(request_body, REQUEST_BODY_SCHEMA)
            except jsonschema.exceptions.ValidationError as e:
                raise ValueError(f"[OpenAPI spec error in request_body] {e.message}")

        if responses:
            try:
                jsonschema.validate(responses, RESPONSES_SCHEMA)
            except jsonschema.exceptions.ValidationError as e:
                raise ValueError(f"[OpenAPI spec error in responses] {e.message}")

        @wraps(handler)
        async def wrapped(*args, **kwargs):
            return await handler(*args, **kwargs)

        wrapped.__openapi__ = {
            "summary": summary,
            "description": description,
            "tags": tags or [],
            "responses": responses or {},
        }

        if request_body:
            wrapped.__openapi__["requestBody"] = request_body

        return wrapped

    return decorator


def build_openapi_spec(app):
    paths = {}

    for route in app.router.routes():
        if not hasattr(route, "handler"):
            continue
        handler = route.handler
        if not hasattr(handler, "__openapi__"):
            continue

        method = (
            list(route.method)[0].lower()
            if isinstance(route.method, set)
            else route.method.lower()
        )
        path = route.resource.canonical

        if path not in paths:
            paths[path] = {}

        paths[path][method] = handler.__openapi__

    return {
        "openapi": "3.0.0",
        "info": {"title": "My API", "version": "1.0.0"},
        "paths": paths,
    }


async def openapi_json(request):
    spec = build_openapi_spec(request.app)
    return web.json_response(spec)


async def swagger_ui(request):
    swagger = """
    <!doctype html>
    <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <title>Swagger UI</title>
            <link
                rel="stylesheet"
                href="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui.css"
            />
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-bundle.js"></script>
            <script>
                SwaggerUIBundle({
                    url: "/openapi.json",
                    dom_id: "#swagger-ui",
                });
            </script>
        </body>
    </html>
    """
    return web.Response(text=swagger, content_type="text/html")
