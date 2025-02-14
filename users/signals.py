# user.signals

from django.db.models.signals import post_save, user_logged_in
from django.dispatch import receiver
from django.utils.timezone import now
from datetime import timedelta
from .models import Profile
from gameplay.models import ActivityTimer
from character.models import Character
from django.contrib.auth import get_user_model
from .utils import assign_character_to_profile

User=get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a profile for the user when a new user is created"""
    if created:
        profile = Profile.objects.create(user=instance)
        ActivityTimer.objects.create(profile=profile)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Save the profile when the user is saved"""
    instance.profile.save()

@receiver(post_save, sender=Profile)
def assign_character(sender, instance, created, **kwargs):
    """Create character when profile saved if not already existing"""
    if created:
        assign_character_to_profile(instance)

@receiver(user_logged_in)
def update_login_streak(sender, request, user, **kwargs):
    profile = user.profile
    today = now().date()

    if profile.last_login.date() == today:
        return  # Already logged in today, no update needed

    if profile.last_login.date() == today - timedelta(days=1):
        profile.login_streak += 1  # Continue the streak
    else:
        profile.login_streak = 1  # Reset streak

    profile.last_login = now()
    profile.save()