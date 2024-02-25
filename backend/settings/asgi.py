"""
ASGI config for neuroezotericabackend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
from django import setup as setup_django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')

setup_django()
asgi = get_asgi_application()

from .urls import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": asgi,
    "websocket": URLRouter(websocket_urlpatterns), # CookieMiddleware(SessionMiddleware(URLRouter(websocket_urlpatterns))),
})
