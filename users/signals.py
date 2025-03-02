# user.signals

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from datetime import timedelta
from .models import Profile
from gameplay.models import ActivityTimer
from character.models import Character
from .utils import assign_character_to_profile
import logging

logger = logging.getLogger("django")

User=get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a profile for the user when a new user is created"""
    if created:
        logger.info(f"New user created: {instance}")
        profile = Profile.objects.create(user=instance)
        ActivityTimer.objects.create(profile=profile)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Save the profile when the user is saved"""
    instance.profile.save()

@receiver(post_save, sender=Profile)
def assign_character(sender, instance, created, **kwargs):
    """Assign character when profile created"""
    if created:
        assign_character_to_profile(instance)

@receiver(user_logged_in)
def update_login_streak(sender, request, user, **kwargs):
    profile = user.profile
    today = now().date()

    logger.info(f"[UPDATE LOGIN STREAK] Updating login streak for {user.username}. Last login: {profile.last_login}")

    if profile.last_login.date() == today:
        logger.debug(f"[UPDATE LOGIN STREAK] Profile {profile.id} already logged in today. No update needed.")
        return
    elif profile.last_login.date() == today - timedelta(days=1):
        profile.login_streak += 1  # Continue the streak
        logger.debug(f"[UPDATE LOGIN STREAK] Profile {profile.id} logged in two days in a row.")
    else:
        profile.login_streak = 1  # Reset streak
        logger.debug(f"[UPDATE LOGIN STREAK] Profile {profile.id} missed a day. Resetting login streak.")

    profile.last_login = now()
    profile.save()
    logger.debug(f"[UPDATE LOGIN STREAK] Updated login streak for profile {profile.id}: {profile.login_streak}")