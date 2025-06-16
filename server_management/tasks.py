from celery import shared_task
from django.utils import timezone
import subprocess

from .models import MaintenanceWindow


@shared_task
def activate_maintenance():
    subprocess.run(["python", "server_management/scripts/activate_maintenance.py"])

@shared_task
def deactivate_maintenance():
    subprocess.run(["python", "server_management/scripts/deactivate_maintenance.py"])

@shared_task
def send_warning():
    print("⚠️ Warning: Scheduled maintenance is approaching!")
    # Add toast notification logic here
