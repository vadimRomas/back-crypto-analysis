from django.urls import re_path

from . import websockets

websocket_urlpatterns = [
    re_path("ws/chat/lobby/", websockets.ChatConsumer.as_asgi()),
]
