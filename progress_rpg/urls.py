"""
URL configuration for progress_rpg project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponseNotFound
from django.urls import re_path, path, include
from django.views.generic import TemplateView

#from gameplay.admin import custom_admin_site

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('admin/timers/', custom_admin_site.urls),
    
    #path('users/', include('users.urls')),
    path('', include('users.urls')),
    path('', include('gameplay.urls')),
    path('', include('payments.urls')),
    path('', include('gameworld.urls')),
    path('', include('server_management.urls')),
    path('', TemplateView.as_view(template_name='users/index.html'), name='index'),  # Add a path for the index page
    re_path(r'^\.well-known/.*$', lambda request: HttpResponseNotFound()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

""" # Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) """