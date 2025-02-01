from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile
from gameplay.models import Character, DailyStats
from django.contrib.auth import get_user_model
from gameplay.utils import assign_character_to_profile

User=get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a profile for the user when a new user is created"""
    if created:
        Profile.objects.create(user=instance)
        #dailystat = DailyStats.objects.get(recordDate=now().date())

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Save the profile when the user is saved"""
    instance.profile.save()

@receiver(post_save, sender=Profile)
def assign_character(sender, instance, created, **kwargs):
    """Create character when profile saved if not already existing"""
    if created:
        assign_character_to_profile(instance)
