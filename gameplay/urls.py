from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('game/', views.game_view, name='game'),
    path('choose_quest/', views.choose_quest, name='choose_quest'),
    path('create_activity_timer/', views.create_activity_timer, name='create_activity_timer'),
    path('start_timer/', views.start_timer, name='start_timer'),
    path('stop_timer/', views.stop_timer, name='stop_timer'),
    path('get_timer_state/', views.get_timer_state, name='get_timer_state'),
    path('submit_activity/', views.submit_activity, name='submit_activity'),
    path('quest_completed/', views.quest_completed, name='quest_completed'),
    path('fetch_quests/', views.fetch_quests, name='fetch_quests'),
    path('fetch_activities/', views.fetch_activities, name='fetch_activities'),
    path('fetch_info/', views.fetch_info, name='fetch_info'),
    path('get_game_statistics', views.get_game_statistics, name='get_game_statistics'),
    path('heartbeat/', views.heartbeat, name='heartbeat'),
]

