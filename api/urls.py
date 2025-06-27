
from dj_rest_auth import urls as auth_urls
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    me_view, 
    CustomRegisterView,
    confirm_email_and_redirect,
    OnboardingViewSet,
    FetchInfoAPIView, 
    ProfileViewSet, 
    CharacterViewSet, 
    ActivityTimerViewSet, 
    QuestTimerViewSet, 
    ActivityViewSet, 
    QuestViewSet, 
    DownloadUserDataAPIView, 
    DeleteAccountAPIView,
    CustomTokenObtainPairView,
    test_post_view,
)

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'character', CharacterViewSet, basename='character')
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'quests', QuestViewSet, basename='quest')
router.register(r'activity_timers', ActivityTimerViewSet, basename='activitytimer')
router.register(r'quest_timers', QuestTimerViewSet, basename='questtimer')
router.register(r'onboarding', OnboardingViewSet, basename='onboarding')


urlpatterns = [
    path('', include(router.urls)),
    path('me/', me_view, name='me'),
    path('fetch_info/', FetchInfoAPIView.as_view(), name='fetch_info'),
    path('auth/confirm-email/<str:key>/', confirm_email_and_redirect, name='account_confirm_email'),
    path('auth/', include(auth_urls)),
    path('auth/', include('users.urls')),

    path('auth/jwt/create/', CustomTokenObtainPairView.as_view(), name='jwt_create'),
    path('auth/jwt/refresh/', TokenRefreshView.as_view(), name='jwt_refresh'),
    path('auth/jwt/verify/', TokenVerifyView.as_view(), name='jwt_verify'),
    path('auth/registration/', CustomRegisterView.as_view(), name='custom_register'),
    path('download_user_data/', DownloadUserDataAPIView.as_view(), name='api_download_user_data'),
    path('delete_account/', DeleteAccountAPIView.as_view(), name='api_delete_account'),

    path('auth/test_post/', test_post_view, name='test_post'),
]