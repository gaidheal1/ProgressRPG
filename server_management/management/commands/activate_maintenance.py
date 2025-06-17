from django.core.management.base import BaseCommand
from server_management.models import MaintenanceWindow

class Command(BaseCommand):
    help = "Activates maintenance mode"

    def handle(self, *args, **kwargs):
        window = MaintenanceWindow.objects.first()  # Example logic
        print(f"Activating maintenance for: {window.name}")