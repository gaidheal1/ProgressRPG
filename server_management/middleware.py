from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from server_management.models import MaintenanceWindow
from django.utils.timezone import now
from django.http import HttpResponseRedirect
























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
            
            
            exempt_paths = ['/logout/', '/static/', '/admin/', '/healthcheck/', '/maintenance/']
            if any(request.path.rstrip('/').startswith(exempt.rstrip('/')) for exempt in exempt_paths):
                print (f"Successful exemption for  {request.path}")
                return self.get_response(request)
            
            return redirect('maintenance')

        return self.get_response(request)