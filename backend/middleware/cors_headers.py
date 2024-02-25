from typing import Callable
from django.conf import settings
from django.http import HttpRequest, HttpResponse


class CrossOriginHeaderMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        response = self.get_response(request)
        
        allowed_origins = settings.CORS_ALLOW_ORIGIN
        if allowed_origins:
            response["Access-Control-Allow-Origin"] = ",".join(allowed_origins)
        
        allowed_headers = settings.CORS_ALLOW_HEADERS
        if allowed_headers:
            response["Access-Control-Allow-Headers"] = ",".join(allowed_headers)
        
        return response
    