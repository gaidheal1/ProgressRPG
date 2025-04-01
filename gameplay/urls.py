from django.urls import path

from . import views

urlpatterns = [
    path('game/', views.game_view, name='game'),
    path('choose_quest/', views.choose_quest, name='choose_quest'),
    path('create_activity/', views.create_activity, name='create_activity'),
    path('submit_activity/', views.submit_activity, name='submit_activity'),
    path('complete_quest/', views.complete_quest, name='complete_quest'),
    path('fetch_quests/', views.fetch_quests, name='fetch_quests'),
    path('fetch_activities/', views.fetch_activities, name='fetch_activities'),
    path('fetch_info/', views.fetch_info, name='fetch_info'),
    path('submit_bug_report/', views.submit_bug_report, name='submit_bug_report'),
]

