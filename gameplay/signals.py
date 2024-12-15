from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Character, Activity
from users.models import Profile
from datetime import datetime, timedelta
#from django.contrib.auth import get_user_model


# @receiver(post_save, sender=Profile)
# def create_character(sender, instance, created, **kwargs):
#     """Create a profile for the user when a new user is created"""
#     if created:
#         Character.objects.create(profile=instance)

@receiver(post_save, sender=Activity)
def add_activity_to_profile(sender, instance, created, **kwargs):
    """Add activity details to the profile when it's created"""
    if created:
        instance.profile.add_activity(instance.duration, 1)

@receiver(user_logged_in)
def update_login_streak(sender, request, user, **kwargs):
    # Check if user has profile
    if hasattr(user, 'profile'):
        profile = user.profile
        last_login_date = profile.last_login.date()
        current_date = now().date()

        if current_date == last_login_date + timedelta(days=1):
            profile.login_streak += 1
            if profile.login_streak_max < profile.login_streak: 
                profile.login_streak_max = profile.login_streak
        elif current_date > last_login_date + timedelta(days=1):
            profile.login_streak = 1
    profile.last_login = now()
    profile.save()