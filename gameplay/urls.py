from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('game/', views.game_view, name='game'),
    path('choose-quest/', choose-quest, name='choose-quest'),
    path('create-activity-timer/', create-activity-timer, name='create-activity-timer'),
    path('start-activity-timer/', start-activity-timer, name='start-activity-timer'),
    path('stop-activity-timer/', stop-activity-timer, name='stop-activity-timer'),
    path('submit-activity/', submit-activity, name='submit-activity'),
    path('start-quest-timer/', start-quest-timer, name='start-quest-timer'),
    path('stop-quest-timer/', stop-quest-timer, name='stop-quest-timer'),
    path('get-timer-state/', get-timer-state, name='get-timer-state'),
]

