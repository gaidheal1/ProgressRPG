# users/tasks.py

from celery import shared_task

# from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging

# from .models import Profile

User = get_user_model()

logger = logging.getLogger("django")


@shared_task
def perform_account_deletion():
    # Get profiles marked for deletion
    users = User.objects.filter(pending_delete=True, delete_at__lte=timezone.now())

    for user in users:
        # Perform the actual deletion

        user.profile.activities.all().delete()
        logger.info(f"deleted activities for User {user.username} (ID: {user.id})")

        user.profile.delete()
        logger.info(f"deleted profile for User {user.username} (ID: {user.id})")

        user.delete()
        logger.info(f"deleted account for User {user.username} (ID: {user.id})")

        # Log the deletion
        logger.info(f"User {user.username} (ID: {user.id}) was deleted after 14 days.")
