"""
Gameplay Utility Functions

This module provides a variety of utility functions to support the gameplay application. 
It handles tasks such as checking quest eligibility, managing timers, and sending WebSocket 
messages to clients. These functions enhance core gameplay logic and enable real-time 
communication between the server and users.

Functions:
    - check_quest_eligibility(character, profile): Checks which quests a character is eligible for based on their profile and quest history.
    - assign_character_to_profile(profile): Assigns a character to a given profile and initializes quests.
    - send_signup_email(user): Sends a welcome email to a newly registered user.
    - start_server_timers(act_timer, quest_timer): Asynchronously starts the server-side activity and quest timers.
    - pause_server_timers(act_timer, quest_timer): Asynchronously pauses the server-side activity and quest timers.
    - control_timers(profile_id, act_timer, quest_timer): Asynchronously starts or pauses both server and client timers, with WebSocket feedback.
    - process_complete_quest(profile_id, character, act_timer, quest_timer): Completes a quest for a character, handling timers and WebSocket updates.
    - send_group_message(group_name, message): Sends a message to a WebSocket group.

Usage:
These utilities support core gameplay mechanics, such as managing quest eligibility, 
handling timers, and enabling asynchronous communication via Django Channels. 
They also improve the user experience by integrating real-time features and sending user notifications.

Author:
    Duncan Appleby

"""

from asgiref.sync import sync_to_async, async_to_sync
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.db import transaction, connection, IntegrityError
from django.utils.html import escape
from django.utils.timezone import now

from .models import QuestCompletion, Quest, ServerMessage
from .serializers import QuestSerializer, QuestTimerSerializer, ActivitySerializer, ActivityTimerSerializer

from character.serializers import CharacterSerializer
from users.serializers import ProfileSerializer

import logging, json, asyncio

logger = logging.getLogger("django")  # Get the logger for this module

def check_quest_eligibility(character, profile):
    """
    Checks the eligibility of quests for a specific character and profile.

    :param character: The character instance to evaluate quests for.
    :param profile: The profile instance associated with the character.
    :return: A list of eligible quests for the given character and profile.
    """
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
                logger.debug(f"[CHECK QUEST ELIGIBILITY] Quest eligible: {quest}")
                eligible_quests.append(quest)
        else:
            logger.debug(f"[CHECK QUEST ELIGIBILITY] Quest not eligible: {quest}")
    return eligible_quests


def start_server_timers(act_timer, quest_timer):
    """
    Attempts to start server-side activity and quest timers.

    :param act_timer: The activity timer instance to be started.
    :type act_timer: ActivityTimer
    :param quest_timer: The quest timer instance to be started.
    :type quest_timer: QuestTimer
    :return: A tuple where the first value is a boolean indicating success,
        and the second value is a string containing additional information or error details.
    """
    logger.info("[START SERVER TIMERS] Attempting to start server timers")
    logger.info(f"[START SERVER TIMERS] Timers status: activity={act_timer.status}, quest={quest_timer.status}")
 
    # if act_timer.status != "empty" and act_timer.activity is None:
    #     logger.error(f"[START SERVER TIMERS] Timer status is {act_timer.status} but activity empty ({act_timer.activity})")
    #     await sync_to_async(act_timer.reset)()

    #  This scenario shouldn't happen. Just in case though...
    if bool(act_timer.is_active()) ^ bool(quest_timer.is_active()):
        logger.info("[TIMER CHECK] One timer is active while the other is paused. Pausing both")
        logger.debug(f"[TIMER CHECK] Activity Timer: {act_timer.is_active()}, Quest Timer: {quest_timer.is_active()}")
        success = pause_server_timers(act_timer, quest_timer)
        if not success:
            result_text = "[START SERVER TIMERS] Failed to pause timers"
            logger.warning(result_text)
            return False, result_text

    if act_timer.status in ['active', 'paused', 'waiting'] and quest_timer.status in ['active', 'paused', 'waiting']:
        try:
            act_timer.start()
            quest_timer.start()
            result_text = "[START SERVER TIMERS] Timers successfully started"
            logger.info(result_text)
            return True, result_text
        except Exception as e:
            error_text = f"[START SERVER TIMERS] Error starting timers: {e}"
            logger.error(error_text, exc_info=True)
            return False, error_text
    else:
        result_text = f"[START SERVER TIMERS] Timers not in a valid state (activity: {act_timer.status}, quest: {quest_timer.status})"
        logger.info(result_text)
        return False, result_text


def pause_server_timers(act_timer, quest_timer):
    """
    Pauses server-side activity and quest timers.

    :param act_timer: The activity timer instance to be paused.
    :type act_timer: ActivityTimer
    :param quest_timer: The quest timer instance to be paused.
    :type quest_timer: QuestTimer
    :return: A tuple where the first value is a boolean indicating success,
        and the second value is a string containing additional information or error details.
    """
    logger.info("[PAUSE SERVER TIMERS] Pausing server timers")
    logger.info(f"[PAUSE SERVER TIMERS] Timers status before: {act_timer.status}/{quest_timer.status}")
    
    try:
        if act_timer.status not in ["completed", "empty"]:
            act_timer.pause()
            logger.info("[PAUSE SERVER TIMERS] Activity timer successfully paused")
        else:
            result_text = f"[PAUSE SERVER TIMERS] Activity timer NOT paused, status: {act_timer.status}"
            logger.info(result_text)

        if quest_timer.status not in ["completed", "empty"]:
            quest_timer.pause()
            logger.info("[PAUSE SERVER TIMERS] Quest timer successfully paused")
        else:
            logger.info(f"[PAUSE SERVER TIMERS] Quest timer NOT paused, status: {act_timer.status}")
        
        logger.info("[PAUSE SERVER TIMERS] Timers paused (or status is complete/empty)")
        logger.info(f"[PAUSE SERVER TIMERS] Timers status after: {act_timer.status}/{quest_timer.status}")
        
        return True, "Success"
    except Exception as e:
        result_text = f"[PAUSE SERVER TIMERS] Error pausing timers: {e}"
        logger.error(result_text, exc_info=True)
        return False, result_text


async def control_timers(profile, act_timer, quest_timer, mode):
    """
    Starts or pauses timers for a specific profile by controlling server-side timers.

    :param profile: The profile the timers.
    :type profile: Profile
    :param act_timer: The activity timer instance.
    :type act_timer: ActivityTimer
    :param quest_timer: The quest timer instance.
    :type quest_timer: QuestTimer
    :param mode: Should be "start" or "pause".
    :type mode: str
    :return: None.
    """
    profile_id = profile.id
    logger.info(f"[CONTROL TIMERS] Performing '{mode}' on timers for profile {profile_id}")

    if mode == "start":
        server_success, result_text = await database_sync_to_async(start_server_timers)(act_timer, quest_timer)
        action = "start_timers"
        success_message = "Timers successfully started"
        failure_message = "Starting timers failed"
    elif mode == "pause":
        server_success, result_text = await database_sync_to_async(pause_server_timers)(act_timer, quest_timer)
        action = "pause_timers"
        success_message = "Timers successfully paused"
        failure_message = "Pausing timers failed"
    else:
        logger.warning(f"[CONTROL TIMERS] Invalid mode: {mode}")

    if server_success:
        logger.info(f"[CONTROL TIMERS] {success_message} for profile {profile_id}")
        await send_group_message(f"profile_{profile_id}", {"type": "action", "action": action, "success": True})
    else:
        logger.warning(f"[CONTROL TIMERS] {failure_message} for profile {profile_id}")
        await send_group_message(f"profile_{profile_id}", {
            "type": "server_message",
            "action": "console.log",
            "message": result_text,
        })


def server_quest_ready(quest_timer):
    """
    Checks if server quest timer is (nearly) complete.
    :param quest_timer: Quest timer
    :type quest_timer: QuestTimer
    :return: True if the quest is nearly complete, False otherwise
    :rtype: bool
    """
    if not quest_timer.status == "complete":
        if quest_timer.get_remaining_time() >= 4:
            return False
        else:
            return True


def process_initiation(profile, character, action):
    """
    Processes the initiation of an activity or quest, starting timers if possible.

    :param profile: The profile associated with the quest.
    :type profile: Profile
    :param character: The character instance completing the quest.
    :type character: Character
    :param act_timer: The activity timer instance.
    :type act_timer: ActivityTimer
    :param quest_timer: The quest timer instance.
    :type quest_timer: QuestTimer
    :param action: The action being performed (e.g., "create_activity" or "choose_quest").
    :type action: str
    :return: True if the quest is successfully completed, False otherwise.
    :rtype: bool
    """
    profile_id = profile.id
    act_timer = profile.activity_timer
    quest_timer = character.quest_timer
    logger.info(f"[PROCESS INITIATION] Initiating {action} for profile {profile_id}, character {character.id}")
    logger.info(f"[PROCESS INITIATION] Timers status: {act_timer.status}/{quest_timer.status}")
    #if action == "quest_complete":
    #    ready = server_quest_ready(quest_timer)
    #else: ready = True
    ready = True

    if ready:
        start_success, result_text = start_server_timers(act_timer, quest_timer)
        if not start_success:
            logger.warning(f"[PROCESS INITIATION] Failed to start timers for profile {profile_id}")
            async_to_sync(send_group_message)(f"profile_{profile_id}", {
                "type": "error",
                "action": "warn",
                "message": "Starting timers failed"
            })
            return False
        else: # Success
            act_timer.refresh_from_db()
            quest_timer.refresh_from_db()
            async_to_sync(send_group_message)(f"profile_{profile_id}", {
                "type": "action",
                "action": "create_activity" if action == "create_activity" else "choose_quest",
            })
            return True
    
    # else:
    #     logger.warning(f"[PROCESS INITIATION] Quest not ready for completion")
    #     serialized_timer = QuestTimerSerializer(quest_timer).data
    #     async_to_sync(send_group_message)(f"profile_{profile_id}", {"type": "action", "action": "correct_timer", "data": serialized_timer})
    #     return False

    return

def process_completion(profile, character, action):
    """
    Processes the completion of an activity or quest, pausing timers.

    :param profile: The profile associated with the quest.
    :type profile: Profile
    :param character: The character instance completing the quest.
    :type character: Character
    :param act_timer: The activity timer instance.
    :type act_timer: ActivityTimer
    :param quest_timer: The quest timer instance.
    :type quest_timer: QuestTimer
    :param action: The action being performed (e.g., "quest_complete" or "submit_activity").
    :type action: str
    :return: True if the quest is successfully completed, False otherwise.
    :rtype: bool
    """
    profile_id = profile.id
    act_timer = profile.activity_timer
    quest_timer = character.quest_timer
    logger.info(f"[PROCESS COMPLETION] Doing {action} for profile {profile_id}, character {character.id}")
    
    if action == "complete_quest":
        ready = server_quest_ready(quest_timer)
        logger.info(f"[PROCESS COMPLETION] Ready is: {ready}")
    else: ready = True

    if ready:
        pause_success, result_text = pause_server_timers(act_timer, quest_timer)
        if not pause_success:
            logger.warning(f"[PROCESS COMPLETION] Failed to pause timers for profile {profile_id}")
            async_to_sync(send_group_message)(f"profile_{profile_id}", {
                "type": "error",
                "action": "warn",
                "message": "Pausing timers failed"
            })
            return False
        else: # Success
            #act_timer.refresh_from_db()
            #quest_timer.refresh_from_db()
            async_to_sync(send_group_message)(f"profile_{profile_id}", {
                "type": "action",
                "action": "quest_complete" if action == "complete_quest" else "submit_activity",
            })
            return True
    
    else: # Quest timer not near enough to completion
        logger.warning(f"[PROCESS COMPLETION] Quest not ready for completion")
        serialized_timer = QuestTimerSerializer(quest_timer).data
        async_to_sync(send_group_message)(f"profile_{profile_id}", {"type": "action", "action": "correct_timer", "data": serialized_timer})
        return False


async def send_group_message(group_name, message):
    # """
    # Sends a message to a WebSocket group.

    # :param group_name: The name of the WebSocket group to send the message to.
    # :type group_name: str
    # :param message: The message to send, as a dictionary.
    # :type message: dict
    # :return: True if the message is successfully sent, False otherwise.
    # """
    logger.info(f"[SEND GROUP MESSAGE] Sending message to group {group_name}. Message type: {message.get('type')}, action: {message.get('action')}, message: {message.get('message')}\ndata: {message.get('data')}\n")

    if message.get("type") in ["event", "notification", "response"]:
        logger.info("[SEND GROUP MESSAGE] Wrapping message in 'server message' type")
        message = {
            "type": "server.message",
            "data": message
        }
    elif message.get("type") == "action":
        logger.info(f"[SEND GROUP MESSAGE] Action type. Message instance type: {type(message)}")

    channel_layer = get_channel_layer()
    logger.info(f"[SEND GROUP MESSAGE] Channel layer: {channel_layer}")
    if channel_layer is not None:
        try:
            sent = await channel_layer.group_send("profile_1", message)
            logger.info(f"[SEND GROUP MESSAGE] Data sent to group 'profile_1': {message}. Sent status: {sent}")
            return True
        except ConnectionError as e:
            logger.error(f"[SEND GROUP MESSAGE] Connection error sending data to group '{group_name}': {e}")
        except ValueError as e:
            logger.error(f"[SEND GROUP MESSAGE] Value error in message format for group '{group_name}': {e}")
        except Exception as e:
            logger.exception(f"[SEND GROUP MESSAGE] Unexpected error sending to group '{group_name}': {e}")
        return False
    else:
        logger.warning(f"[GROUP SEND MESSAGE] No channel layer available for group '{group_name}'")
        return False


