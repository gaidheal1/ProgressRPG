from character.models import Character, PlayerCharacterLink
from django.utils.timezone import now
from django.db import transaction, connection, IntegrityError
from django.utils.html import escape
from channels.db import database_sync_to_async
from .models import QuestCompletion, Quest, Activity, ActivityTimer, QuestTimer
from .serializers import QuestSerializer, QuestTimerSerializer, ActivitySerializer, ActivityTimerSerializer
from character.serializers import CharacterSerializer
from users.serializers import ProfileSerializer
from channels.layers import get_channel_layer
import asyncio
from asgiref.sync import sync_to_async
import logging, json

logger = logging.getLogger("django")  # Get the logger for this module

def check_quest_eligibility(character, profile):
    logger.info(f"[CHECK QUEST ELIGIBILITY] Checking eligibility for character {character.id} and profile {profile.id}")
    char_quests = QuestCompletion.objects.filter(character=character)
    quests_done = {}
    for completion in char_quests:
        quests_done[completion.quest] = completion.times_completed
        logger.debug(f"[CHECK QUEST ELIGIBILITY] Quest {completion.quest} completed {completion.times_completed} times")
    all_quests = Quest.objects.all()

    eligible_quests = []
    for quest in all_quests:
        logger.debug(f"[CHECK QUEST ELIGIBILITY] Evaluating quest: {quest}")

        # Test for eligibility
        if quest.checkEligible(character, profile) and \
            quest.not_repeating(character) and \
            quest.requirements_met(quests_done):
                logger.info(f"[CHECK QUEST ELIGIBILITY] Quest eligible: {quest}")
                eligible_quests.append(quest)
        else:
            logger.debug(f"[CHECK QUEST ELIGIBILITY] Quest not eligible: {quest}")
    return eligible_quests


async def start_server_timers(act_timer, quest_timer):
    logger.info("[START SERVER TIMERS] Attempting to start server timers")
    logger.debug(f"[START SERVER TIMERS] Timers status: activity={act_timer.status}, quest={quest_timer.status}")
 
    if act_timer.status in ['active', 'paused', 'waiting'] and quest_timer.status in ['active', 'paused', 'waiting']:
        try:
            await sync_to_async(act_timer.start)()
            await sync_to_async(quest_timer.start)()
            logger.info("[START SERVER TIMERS] Timers successfully started")
            return True
        except Exception as e:
            logger.error(f"[START SERVER TIMERS] Error starting timers: {e}", exc_info=True)
            return False
    else:
        logger.info(f"[START SERVER TIMERS] Timers not in a valid state (activity: {act_timer.status}, quest: {quest_timer.status})")
        return False


async def start_timers(profile_id, act_timer, quest_timer):
    logger.info(f"[START TIMERS] Starting timers for profile {profile_id}")
    
    server_success = await start_server_timers(act_timer, quest_timer)

    if server_success:
        logger.info(f"[START TIMERS] Timers successfully started for profile {profile_id}")
        await send_group_message(f"profile_{profile_id}", {"action": "start_timers", "success": True})
    else:
        logger.warning(f"[START TIMERS] Failed to start timers for profile {profile_id}")
        await send_group_message(f"profile_{profile_id}", {"action": "start_timers", "success": False})



async def pause_server_timers(act_timer, quest_timer):
    logger.info("[PAUSE SERVER TIMERS] Pausing server timers")
    logger.debug(f"[PAUSE SERVER TIMERS] Timers status: {act_timer.status}/{quest_timer.status}")
    
    try:
        await sync_to_async(act_timer.pause)()
        await sync_to_async(quest_timer.pause)()
        logger.info("[PAUSE SERVER TIMERS] Timers successfully paused")
        return True
    except Exception as e:
        logger.error(f"[PAUSE SERVER TIMERS] Error pausing timers: {e}", exc_info=True)
        return False


async def pause_timers(profile_id, act_timer, quest_timer):
    logger.info(f"[PAUSE TIMERS] Pausing timers for profile {profile_id}")
    
    server_success = await pause_server_timers(act_timer, quest_timer)
    
    if server_success:
        logger.info(f"[PAUSE TIMERS] Timers successfully paused for profile {profile_id}")
        await send_group_message(f"profile_{profile_id}", {"action": "pause_timers", "success": True})
    else:
        logger.warning(f"[PAUSE TIMERS] Failed to pause timers for profile {profile_id}")
        await send_group_message(f"profile_{profile_id}", {"action": "pause_timers", "success": False})


async def send_group_message(group_name, message):
    """
    Sends a message to a WebSocket group.
    
    :param group_name: The name of the WebSocket group to send the message to.
    :param message: The message to send, as a dictionary.
    """
    logger.info(f"[SEND GROUP MESSAGE] Sending message to group {group_name}")
    channel_layer = get_channel_layer()
    if channel_layer is not None:
        try:
            # Send the message to the group
            await channel_layer.group_send(
                group_name,
                {
                    "type": "group.message",
                    "data": message
                }
            )
            logger.debug(f"Data sent to group '{group_name}': {data}")
        except Exception as e:
            logger.error(f"Error sending data to group '{group_name}': {e}")