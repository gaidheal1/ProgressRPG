import django
import os
import subprocess
from django.utils import timezone
from server_management.models import MaintenanceWindow

import sys

sys.path.append("/mnt/c/users/duncan/onedrive/documents/coding-projects/progress_rpg")

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.getenv("DJANGO_SETTINGS_MODULE", "progress_rpg.settings.dev"),
)
django.setup()


def activate_maintenance():
    now = timezone.now()
    window = MaintenanceWindow.objects.filter(
        start_time__lte=now, end_time__gte=now
    ).first()

    if window.exists():
        print("Activating maintenance mode...")
        subprocess.run(["python", "manage.py", "pause_timers"])
        window.is_active = True
        # Add any additional activation logic here.


if __name__ == "__main__":
    activate_maintenance()
