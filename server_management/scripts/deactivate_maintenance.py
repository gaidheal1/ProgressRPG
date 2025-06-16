import django
import os
from django.utils import timezone
from server_management.models import MaintenanceWindow
from gameplay.models import ActivityTimer, QuestTimer  # Adjust based on actual model location

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'progress_rpg.settings')
django.setup()

def deactivate_maintenance():
    now = timezone.now()

    active_window = MaintenanceWindow.objects.filter(start_time__lte=now, end_time__gte=now).order_by('-start_time').first()

    if not active_window.exists():
        print("No active maintenance window. Skipping deactivation.")
        return

    # Mark maintenance windows as completed
    active_window.is_active = False
    active_window.update(end_time=now)  # Optional: adjust end time to match deactivation moment

    print(f"Deactivated maintenance mode.")

if __name__ == "__main__":
    deactivate_maintenance()