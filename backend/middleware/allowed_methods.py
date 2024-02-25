from django.http import HttpRequest
import orjson

from web import CustomJsonResponse
from .base import wrap_middleware


def allowed_methods(*methods: str):
    assert methods
    methods = [m.upper() for m in methods]
    
    async def middleware(request: HttpRequest, next):
        if request.method not in methods:
            resp = CustomJsonResponse({ "type": "method_not_allowed" }, status = 405)
        else:
            if request.method != "GET":
                request.DATA = {}
                if (request.headers.get("Content-Type", None) == "application/json" and request.body):
                    try:
                        request.DATA = orjson.loads(request.body)
                    except:
                        pass
                
            resp = await next()
        resp["Access-Control-Allow-Methods"] = ",".join(methods)
        return resp
        
    return wrap_middleware(middleware)
