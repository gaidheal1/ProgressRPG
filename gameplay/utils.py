from .models import Character

def create_character_for_profile(profile):
    """Utility function to create a Character for a Profile"""
    Character.objects.create(profile=profile)