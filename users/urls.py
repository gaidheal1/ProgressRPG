from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .views import RegisterView, LoginView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),  # Use auth_views
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('edit_profile/', views.edit_profile_view, name='edit_profile'),
    path('create_profile/', views.create_profile_view, name='create_profile'),
    path('link_character/', views.link_character_view, name='link_character'),
    path('download_user_data/', views.download_user_data, name='download_user_data'),
    path('delete_account', views.delete_account, name='delete_account'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email_plain.txt',
        html_email_template_name='registration/password_reset_email_html.html',
        subject_template_name='registration/password_reset_email_subject.txt',
        ), name='password_reset'),
    path('password_reset/done', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Add other user-related routes
]

