from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import RegisterView

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  # Use auth_views
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('edit_profile/', views.edit_profile_view, name='edit_profile'),
    path('create_profile/', views.create_profile_view, name='create_profile'),
    path('create_character/', views.create_character_view, name='create_character'),
    path('download_user_data/', views.download_user_data, name='download_user_data'),
    path('delete_account', views.delete_account, name='delete_account'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),


    
    # Add other user-related routes
]

