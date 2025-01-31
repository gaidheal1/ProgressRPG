from django.urls import re_path
import django
django.setup()
from .consumers import ProfileConsumer  



websocket_urlpatterns = [
    re_path(r'ws/profile_(?P<profile_id>\d+)/$', ProfileConsumer.as_asgi()),  # WebSocket endpoint
]
