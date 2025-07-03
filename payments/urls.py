from django.urls import path
from . import views

urlpatterns = [
    path("subscribe/", views.subscribe_view, name="subscribe"),
    # Add other user-related routes
]
