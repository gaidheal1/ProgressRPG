from datetime import datetime, timedelta
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, OperationalError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

from .models import Activity, Quest, QuestResults, ServerMessage
from .utils import send_group_message
from character.models import Character
from users.models import Profile
from events.models import Event, EventContribution

import logging

logger = logging.getLogger("django")


@receiver(post_save, sender=Activity)
def handle_new_activity(sender, instance, created, **kwargs):
    """Handles all activity submission jobs"""
    if created:
        """try:
            logger.info(
                f"[HANDLE NEW ACTIVITY] New activity created: {instance.id}, profile: {instance.profile.id}"
            )
            instance.profile.add_activity(instance.duration, 1)
        except IntegrityError as e:
            logger.error(
                f"[HANDLE NEW ACTIVITY] IntegrityError while adding activity for profile {instance.profile.id}: {e}",
                exc_info=True,
            )
        except ObjectDoesNotExist as e:
            logger.error(
                f"[HANDLE NEW ACTIVITY] ObjectDoesNotExist error for activity {instance.id}: {e}",
                exc_info=True,
            )
        except Exception as e:
            logger.error(
                f"[HANDLE NEW ACTIVITY] Unexpected error for activity {instance.id}: {e}",
                exc_info=True,
            )
        """
        # Event Progress Updates
        """
        try:
            active_events = Event.objects.filter(is_active=True)
            for event in active_events:
                event_progress, _ = EventContribution.objects.get_or_create(
                    event=event, user=instance.user
                )
                event_progress.total_time += instance.duration_seconds
                event_progress.save()
                logger.info(f"[HANDLE NEW ACTIVITY] Updated event progress for user {instance.user.id}, event: {event.id}")
        except Exception as e:
            logger.error(f"[HANDLE NEW ACTIVITY] Error updating event progress for activity {instance.id}: {e}", exc_info=True)
        """


@receiver(user_logged_in)
def update_login_streak(sender, request, user, **kwargs):
    """Updates the user's login streak."""
    if hasattr(user, "profile"):
        profile = user.profile
        try:
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
            logger.debug(
                f"[UPDATE LOGIN STREAK] Login streak updated for profile {profile.id}: streak {profile.login_streak}, max streak {profile.login_streak_max}"
            )
        except Exception as e:
            logger.error(
                f"[UPDATE LOGIN STREAK] Error updating login streak for user {user.id}: {e}",
                exc_info=True,
            )


@receiver(post_save, sender=Quest)
def create_quest_results(sender, instance, created, **kwargs):
    """Creates QuestResults for new quests."""
    if created:
        try:
            QuestResults.objects.create(quest=instance)
            logger.info(
                f"[CREATE QUEST RESULTS] Quest results created for quest: {instance.id}"
            )
        except IntegrityError as e:
            logger.error(
                f"[CREATE QUEST RESULTS] IntegrityError while creating quest results for quest {instance.id}: {e}",
                exc_info=True,
            )
        except Exception as e:
            logger.error(
                f"[CREATE QUEST RESULTS] Unexpected error while creating quest results for quest {instance.id}: {e}",
                exc_info=True,
            )


@receiver(post_save, sender=ServerMessage)
def server_message_created(sender, instance, created, **kwargs):
    """Triggers consumer to run message send method when a new server message is created."""
    if created and not instance.is_draft:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        async_to_sync(send_group_message)(
            instance.group, {"type": "send_pending_messages"}
        )
