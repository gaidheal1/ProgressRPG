from django.urls import path
from .views import dashboard_view, game_view, get_game_statistics, ActivityListCreateView, ActivityDetailView, SkillListCreateView, SkillDetailView, ProjectListCreateView, ProjectDetailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('game/', game_view, name='game'),
    path('get_game_statistics', get_game_statistics, name='get_game_statistics'),

    path('api/activities/', ActivityListCreateView.as_view(), name='activity-list-create'),
    path('api/activities/<int:pk>/', ActivityDetailView.as_view(), name='activity-detail'),
    path('api/skills/', SkillListCreateView.as_view(), name='skill-list-create'),
    path('api/skills/<int:pk>/', SkillDetailView.as_view(), name='skill-detail'),
    path('api/projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('api/projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('api/token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token-refresh'),
]

