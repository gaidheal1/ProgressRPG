from django.db import models
from django.utils import timezone
import subprocess
from celery import Celery
from django.shortcuts import redirect












class MaintenanceWindow(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True)
    tasks_scheduled = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    def mark_tasks_scheduled(self):
        self.tasks_scheduled = True
        self.save()

    def activate_maintenance(self):
        now = timezone.now()
        print("Activating maintenance mode...")
        subprocess.run(["python", "manage.py", "pause_timers"])
        self.is_active = True
        self.save()
        # Add any additional activation logic here.
        
    def deactivate_maintenance(self):
        now = timezone.now()
        print("Deactivating maintenance mode... wrapping up!")
        self.is_active = False
        self.save()
        # Add any additional activation logic here.

    def schedule_tasks(self):
        """Schedules Celery tasks if not already scheduled."""
        now = timezone.now()
        if self.tasks_scheduled:
            return False  # Prevent duplicate scheduling
        if self.end_time < now:
            return False

        from server_management.tasks import activate_maintenance, send_warning

        activate_maintenance.apply_async(eta=self.start_time)
        send_warning.apply_async(eta=self.start_time - timezone.timedelta(minutes=30))
        send_warning.apply_async(eta=self.start_time - timezone.timedelta(minutes=10))
        send_warning.apply_async(eta=self.start_time - timezone.timedelta(minutes=5))

        self.tasks_scheduled = True
        self.save()
        return True

    def delete_scheduled_tasks(self):
        """Deletes scheduled tasks if necessary."""
        from celery.task.control import revoke
        # Logic to track and revoke tasks (requires storing task IDs)
        self.tasks_scheduled = False
        self.save()
