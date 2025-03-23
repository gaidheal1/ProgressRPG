from django.urls import re_path
import django

websocket_urlpatterns = []

def load_websocket_urlpatterns():
    from .consumers import TimerConsumer  
    global websocket_urlpatterns
    websocket_urlpatterns = [
        re_path(r'ws/profile_(?P<profile_id>\d+)/$', TimerConsumer.as_asgi()),  # WebSocket endpoint
    ]

load_websocket_urlpatterns()