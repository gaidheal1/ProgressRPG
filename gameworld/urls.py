from django.urls import path
from . import views

urlpatterns = [
    path("game_statistics/", views.get_game_statistics, name="game_statistics"),
]
