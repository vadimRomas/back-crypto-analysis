from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path, re_path

import apps
from apps.cripto_info.routing import websocket_urlpatterns
from apps.cripto_info.views import PracticeConsumer, TextRoomConsumer

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests

    # WebSocket chat handler
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
