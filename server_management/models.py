from django.db import models
from django.utils import timezone
import subprocess
from celery import Celery
from django.shortcuts import redirect
import logging
from asgiref.sync import async_to_sync
from gameplay.utils import send_group_message
logger = logging.getLogger("django")


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


    def schedule_tasks(self):
        """Schedules Celery tasks if not already scheduled."""
        logger.info("[SCHEDULE TASKS] Scheduling maintenance window tasks")
        now = timezone.now()
        if self.tasks_scheduled:
            return False  # Prevent duplicate scheduling
        if self.end_time < now:
            return False

        from server_management.tasks import send_warning, activate_maintenance

        warning_times = [30, 15, 10, 5, 3, 2, 1]  # List of warning times in minutes
        for minutes_until in warning_times:
            message = f"Warning: maintenance is starting in {minutes_until} minute(s)!"
            send_warning.apply_async(
                kwargs={"message": message}, 
                eta=self.start_time - timezone.timedelta(minutes=minutes_until)
            )
        logger.debug(f"[SCHEDULE TASKS] Scheduled {len(warning_times)} maintenance warnings")

        activate_maintenance.apply_async(
            kwargs={"window_id": self.id},
            eta=self.start_time
        )
        logger.debug(f"[SCHEDULE TASKS] Scheduled maintenance window to start at {self.start_time}")

        self.tasks_scheduled = True
        self.save()
        return True
    

    def activate_maintenance(self):
        logger.info("[ACTIVATE MAINTENANCE] Activating maintenance mode...")
        now = timezone.now()
        subprocess.run(["python", "manage.py", "pause_timers"])
        async_to_sync(send_group_message)("online_users", {"type": "action", "action": "refresh", "success": True})
        
        self.is_active = True
        self.save()
        # Add any additional activation logic here.
        
    def deactivate_maintenance(self):
        logger.info("[DEACTIVATE MAINTENANCE] Deactivating maintenance mode...")
        print("Deactivating maintenance mode... wrapping up!")
        self.is_active = False
        self.save()
        # Add any additional activation logic here.


    # def delete_scheduled_tasks(self):
    #     """Deletes scheduled tasks if necessary."""
    #     from celery.task.control import revoke
    #     # Logic to track and revoke tasks (requires storing task IDs)
    #     self.tasks_scheduled = False
    #     self.save()
