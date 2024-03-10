"""
ASGI config for elearning project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import elearning_base.routing
import elearning_base.urls
from django.core.asgi import get_asgi_application

from elearning_base.routing import websocket_urlpatterns 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elearning.settings')

#ASGI configuration file for the elearning project - sets up application routing for HTTP and websocket protocol connections

django_asgi_app = get_asgi_application()
import elearning_base.routing

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(elearning_base.routing.websocket_urlpatterns)))
})

