from django.urls import path
from . import views

urlpatterns = [
    path("maintenance/", views.maintenance_view, name="maintenance"),
]
