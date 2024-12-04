from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Character
from users.models import Profile
#from django.contrib.auth import get_user_model


# @receiver(post_save, sender=Profile)
# def create_character(sender, instance, created, **kwargs):
#     """Create a profile for the user when a new user is created"""
#     if created:
#         Character.objects.create(profile=instance)
