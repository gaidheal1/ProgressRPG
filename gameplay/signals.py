from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Activity, Quest, QuestResults
from character.models import Character
from users.models import Profile
from events.models import Event, EventContribution
from datetime import datetime, timedelta
#from django.contrib.auth import get_user_model

@receiver(post_save, sender=Activity)
def handle_new_activity(sender, instance, created, **kwargs):
    """Handles all activity submission jobs"""
    if created:
        instance.profile.add_activity(instance.duration, 1)

        # Event Progress Updates
        """ active_events = Event.objects.filter(is_active=True)
        for event in active_events:
            event_progress, _ = EventContribution.objects.get_or_create(
                event=event, user=instance.user
            )
            event_progress.total_time += instance.duration_seconds
            event_progress.save() """

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

@receiver(post_save, sender=Quest)
def create_quest_results(sender, instance, created, **kwargs):
    if created:  # Only run when a new Quest is created
        QuestResults.objects.create(quest=instance)