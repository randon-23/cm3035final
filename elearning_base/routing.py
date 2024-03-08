from django.urls import re_path
from . import consumers

# Websocket routing URLs for lobby messages and notifications
websocket_urlpatterns = [
    re_path(r'ws/lobby/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]