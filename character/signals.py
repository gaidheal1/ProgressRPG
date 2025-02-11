# character.signals

from django.db.models.signals import post_save
from django.dispatch import receiver
from gameplay.models import QuestTimer
from .models import Character


@receiver(post_save, sender=Character)
def create_timer(sender, instance, created, **kwargs):
    """Create a quest timer for a new character"""
    if created:
        quest_timer = QuestTimer.objects.create(character=instance)