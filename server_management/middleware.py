from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponseForbidden, HttpResponseRedirect
from server_management.models import MaintenanceWindow
from django.utils.timezone import now
from django.urls import resolve



BLOCKED_USER_AGENTS = ["bot", "crawler", "spider", "scraper", "wget", "curl"]

class BlockBotMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        if any(bot in user_agent for bot in BLOCKED_USER_AGENTS):
            return HttpResponseForbidden("Access denied.")
        return self.get_response(request)




class MaintenanceModeMiddleware:
    """Middleware to restrict access during maintenance, allowing certain users/tests through."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if an active maintenance window exists
        active_window = MaintenanceWindow.objects.filter(is_active=True).first()

        if active_window:
            user = request.user if hasattr(request, "user") else None
            #print(f"User: {request.user}, Authenticated: {request.user.is_authenticated}, Staff: {request.user.is_staff}")
            
            # Allow superusers or staff to bypass maintenance restrictions
            if user and request.user.is_authenticated and request.user.is_staff:
                return self.get_response(request)
            
            exempt_names = ['logout', 'healthcheck', 'maintenance']
            try:
                match = resolve(request.path)
                if match.url_name in exempt_names or request.path.startswith('/static') or request.path.startswith('/admin'):
                    return self.get_response(request)
            except:
                pass  # let maintenance block unknown paths
            
            return redirect('maintenance')

        return self.get_response(request)
