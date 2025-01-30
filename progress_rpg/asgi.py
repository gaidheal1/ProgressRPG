import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from gameplay.routing import websocket_urlpatterns
from gameplay import consumers

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "progress_rpg.settings")
django.setup()

from gameplay.mymiddleware import MyAuthMiddleware
from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Regular HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        ),
    ),
})
