from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('game/', views.game_view, name='game'),
    path('get_game_statistics', views.get_game_statistics, name='get_game_statistics'),
]

