from django.shortcuts import redirect
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
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
        active_window = MaintenanceWindow.objects.filter(is_active=True).first()
        if not active_window:
            return self.get_response(request)

        user = getattr(request, "user", None)
        if user and user.is_authenticated and user.is_staff:
            return self.get_response(request)

        exempt_paths = [
            "/logout/",
            "/static/",
            "/admin/",
            "/healthcheck/",
            "/maintenance/",
            "/api/v1/maintenance_status/",
        ]
        if any(request.path.startswith(exempt) for exempt in exempt_paths):
            return self.get_response(request)

        if request.path.startswith("/api/"):
            return JsonResponse({"detail": "Maintenance mode"}, status=503)

        return redirect("/maintenance/")
