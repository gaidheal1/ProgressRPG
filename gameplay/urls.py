from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('game/', views.game_view, name='game'),
    path('choose_quest/', views.choose_quest, name='choose_quest'),
    path('create_activity_timer/', views.create_activity_timer, name='create_activity_timer'),
    path('start_activity_timer/', views.start_activity_timer, name='start_activity_timer'),
    path('stop_activity_timer/', views.stop_activity_timer, name='stop_activity_timer'),
    path('submit_activity/', views.submit_activity, name='submit_activity'),
    path('create_quest_timer/', views.create_quest_timer, name='create_quest_timer'),
    path('start_quest_timer/', views.start_quest_timer, name='start_quest_timer'),
    path('stop_quest_timer/', views.stop_quest_timer, name='stop_quest_timer'),
    path('quest_completed/', views.quest_completed, name='quest_completed'),
    path('get_timer_state/', views.get_timer_state, name='get_timer_state'),
]

