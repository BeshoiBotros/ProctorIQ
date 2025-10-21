"""
ASGI config for ProctorIQ project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django_channels_jwt_auth_middleware.auth import JWTAuthMiddlewareStack

import proctoring.routing as proctoring_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProctorIQ.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    'websocket': JWTAuthMiddlewareStack(
        URLRouter(
            proctoring_routing.websocket_urlpatterns
        )
    )
})
