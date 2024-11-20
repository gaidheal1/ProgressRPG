from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

urlpatterns = [
    path('/admin/', admin.site.urls),
    path('', include('users.urls')),  # Include users app URLs
    
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)