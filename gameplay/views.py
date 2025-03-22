from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import transaction, connection, IntegrityError
from django.utils import timezone
from django.utils.html import escape
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync, sync_to_async
import json, logging

from .models import Quest, Activity, QuestCompletion, ActivityTimer, QuestTimer
from .serializers import ActivitySerializer, QuestSerializer, ActivityTimerSerializer, QuestTimerSerializer
from .utils import check_quest_eligibility, send_group_message

from character.models import PlayerCharacterLink
from character.serializers import CharacterSerializer

from users.serializers import ProfileSerializer
from users.models import Profile


logger = logging.getLogger("django")



# Dashboard view
@login_required
def dashboard_view(request):
    profile = request.user.profile
    return render(request, 'gameplay/dashboard.html', {'profile': profile})

# Game view
@login_required
def game_view(request):
    """
    Render the main game view for the logged-in user.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :return: An HTML response rendering the game view.
    :rtype: django.http.HttpResponse
    """
    try:
        logger.info(f"[GAME VIEW] Accessed by user {request.user.profile.id}")
        return render(request, 'gameplay/game.html', {"profile": request.user.profile})
    except Exception as e:
        logger.error(f"[GAME VIEW] Error rendering game view for user {request.user.profile.id}: {str(e)}", exc_info=True)
        return JsonResponse({"error": "An error occurred"}, status=500)

# Fetch activities
@login_required
def fetch_activities(request):
    """
    Fetch and return all activities for the logged-in user on the current date.

    :param request: The HTTP GET request object.
    :type request: django.http.HttpRequest
    :return: A JSON response containing the activities or an error message.
    :rtype: django.http.JsonResponse
    """
    if request.method != 'GET':
        logger.warning(f"[FETCH ACTIVITIES] Invalid method {request.method} used by user {request.user.profile.id}")
        return JsonResponse({"error": "Invalid method"}, status=405)

    profile = request.user.profile
    logger.info(f"[FETCH ACTIVITIES] Request received from user {profile.id}")

    try:
        activities = Activity.objects.filter(profile=profile, created_at__date=timezone.now().date())
        serializer = ActivitySerializer(activities, many=True).data
        
        response = {
            "success": True,
            "activities": serializer,
            "message": "Activities fetched"
        }
        logger.debug(f"[FETCH ACTIVITIES] {len(activities)} activities fetched for user {profile.id}")
        return JsonResponse(response)
    except Exception as e:
            logger.error(f"[FETCH ACTIVITIES] Error fetching activities for user {profile.id}: {str(e)}", exc_info=True)
            return JsonResponse({"error": "An error occurred while fetching activities"}, status=500)

    

# Fetch quests
@login_required
def fetch_quests(request):
    """
    Fetch and return eligible quests for the character associated with the logged-in user.

    :param request: The HTTP GET request object.
    :type request: django.http.HttpRequest
    :return: A JSON response containing the eligible quests or an error message.
    :rtype: django.http.JsonResponse
    """
    if request.method != 'GET':
        logger.warning(f"[FETCH QUESTS] Invalid method {request.method} used by user {request.user.profile.id}")
        return JsonResponse({"error": "Invalid method"}, status=405)

    profile = request.user.profile
    logger.info(f"[FETCH QUESTS] Request received from user {profile.id}")
    character = PlayerCharacterLink.get_character(profile)

    try:
        logger.info(f"[FETCH QUESTS] Checking eligible quests for character {character.id}, {profile.id}")
        eligible_quests = check_quest_eligibility(character, profile)
        
        for quest in eligible_quests:
            quest.save()
            logger.debug(f"[FETCH QUESTS] Quest {quest.id} - {quest.name} saved for character {character.id}")

        serializer = QuestSerializer(eligible_quests, many=True).data
        
        response = {
            "success": True,
            "quests": serializer,
            "message": "Eligible quests fetched"
        }
        return JsonResponse(response)
    except Exception as e:
        logger.error(f"[FETCH QUESTS] Error fetching quests for user {profile.id}: {str(e)}", exc_info=True)
        return JsonResponse({"error": "An error occurred while fetching quests"}, status=500)

# Add this to a management command or view for testing
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

async def test_redis_connection():
    channel_layer = get_channel_layer()
    profile_id = 1

    try:
        await channel_layer.group_add("test_group", "test_channel")
        await channel_layer.group_discard("test_group", "test_channel")
        logger.info("Redis connection successful!")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")

    try:
        # Send a test message directly to the group
        await channel_layer.group_send(
            f"profile_{profile_id}",
            {
                "type": "test_message",
                "message": "Testing Redis connection"
            }
        )
        logger.info(f"Test message sent to profile_{profile_id}")
        return True
    except Exception as e:
        logger.error(f"Redis connection test failed: {e}")
        return False
    
# Fetch info
@login_required
def fetch_info(request):
    """
    Retrieve profile, character, activity timer, and quest timer details for the logged-in user.

    :param request: The HTTP GET request object.
    :type request: django.http.HttpRequest
    :return: A JSON response containing the profile, character, and timer information.
    :rtype: django.http.JsonResponse
    """
    if request.method != "GET":
        logger.warning(f"[FETCH INFO] Invalid method {request.method} used by user {request.user.profile.id}")
        return JsonResponse({"error": "Invalid method"}, status=405)
    
    profile = request.user.profile
    character = PlayerCharacterLink.get_character(profile)

    async_to_sync(test_redis_connection)()

    try:
        logger.info(f"[FETCH INFO] Fetching data for profile {profile.id}, character {character.id}")
        logger.info(f"[FETCH INFO] Timers status: {profile.activity_timer.status}/{character.quest_timer.status}")

        qt = character.quest_timer
        if qt.time_finished() and qt.status != "complete":
            logger.warning(f"[FETCH INFO] Quest timer expired for character {character.id}, marking quest as complete")
            qt.elapsed_time = qt.duration
            qt.save()
            logger.info(f"PRAHBLEM qt status {qt.status}, {qt.quest}, elapsed/remaining {qt.get_elapsed_time()}/{qt.get_remaining_time()}, duration {qt.duration}")
            
            async_to_sync(send_group_message)(f"profile_{profile.id}", {"type": "action", "action": "quest_complete"})
            channel_layer = get_channel_layer()
            #async_to_sync(channel_layer.group_send)("profile_1", {"type": "test_message", "message": "Blarp"})
            
        
        if profile.activity_timer.status != "empty" and profile.activity_timer.activity is None:
            logger.error(f"[FETCH INFO] Timer status is {profile.activity_timer.status} but activity empty ({profile.activity_timer.activity}). Resetting activity timer")
            profile.activity_timer.reset()

        profile_serializer = ProfileSerializer(profile).data
        character_serializer = CharacterSerializer(character).data
        act_timer = ActivityTimerSerializer(profile.activity_timer).data
        quest_timer = QuestTimerSerializer(qt).data

        response = {
            "success": True,
            "profile": profile_serializer,
            "character": character_serializer,
            "message": "Profile and character fetched",
            "activity_timer": act_timer,
            "quest_timer": quest_timer,
        }

        logger.debug(f"[FETCH INFO] Response generated successfully for profile {profile.id}")

        return JsonResponse(response)
    
    except Exception as e:
        logger.error(f"[FETCH INFO] Error fetching info for user {profile.id}: {str(e)}", exc_info=True)
        return JsonResponse({"error": "An error occurred while fetching info"}, status=500)
    

# Choose quest
#@transaction.atomic
@login_required
@csrf_exempt
def choose_quest(request):
    """
    Allow the user to select a quest and update the associated quest timer.

    :param request: The HTTP POST request object with quest ID and duration.
    :type request: django.http.HttpRequest
    :return: A JSON response indicating the status of the quest selection.
    :rtype: django.http.JsonResponse
    """
    if request.method != "POST":
        logger.warning(f"[CHOOSE QUEST] Invalid method {request.method} used by user {request.user.profile.id}")
        return JsonResponse({"error": "Invalid request"}, status=400)
    
    if request.headers.get('Content-Type') != 'application/json':
        logger.warning(f"[CHOOSE QUEST] Invalid content type: {request.headers.get('Content-Type')}")
        return JsonResponse({"error": "Invalid content type"}, status=400)
        
    profile = request.user.profile

    try:
        logger.info(f"[CHOOSE QUEST] User {request.user.profile.id} initiated quest selection")
        data = json.loads(request.body)
        quest_id = escape(data.get('quest_id'))
        quest = get_object_or_404(Quest, id=quest_id)
        
        if not quest:
            logger.warning(f"[CHOOSE QUEST] Quest ID {quest_id} not found for user {profile.id}")
            return JsonResponse({"success": False, "message": "Error: quest not found"})
        
        character = PlayerCharacterLink.get_character(profile)
        duration = data.get('duration')

        #with transaction.atomic():
        character.quest_timer.change_quest(quest, duration) # status should be 'waiting' now
        character.quest_timer.refresh_from_db()
        
        logger.info(f"[CHOOSE QUEST] Quest {quest.name} (ID: {quest.id}) selected by user {profile.id}")

        quest_timer = QuestTimerSerializer(character.quest_timer).data
        response = {
            "success": True,
            "quest_timer": quest_timer,
            "message": f"Quest {quest.name} selected",
        }
        
        logger.debug(f"[CHOOSE QUEST] Response generated successfully for user {profile.id}")
        
        return JsonResponse(response)

    except json.JSONDecodeError as e:
        logger.error(f"[CHOOSE QUEST] JSON decode error for user {profile.id}: {e}")
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        logger.exception(f"[CHOOSE QUEST] Unexpected error for user {profile.id}: {e}")
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)
    

@login_required
#@transaction.atomic
@csrf_exempt
def create_activity(request):
    """
    Creates a new activity for the logged-in user and updates the activity timer.

    :param request: The HTTP POST request containing the activity name.
    :type request: django.http.HttpRequest
    :return: A JSON response containing the activity timer details or an error message.
    :rtype: django.http.JsonResponse
    """
    if request.method != "POST":
        logger.warning(f"[CREATE ACTIVITY] Invalid method {request.method} used by user {request.user.profile.id}")
        return JsonResponse({"error": "Invalid method"}, status=405)
    
    profile = request.user.profile

    try:
        logger.info(f"[CREATE ACTIVITY] Profile {profile.id} initiated activity creation")
        data = json.loads(request.body)
        activity_name = escape(data.get("activityName"))

        if not activity_name:
            logger.warning(f"[CREATE ACTIVITY] Activity name missing from request for user {profile.id}")
            return JsonResponse({"error": "Activity name is required"}, status=400)
        
        logger.debug(f"[CREATE ACTIVITY] Received activity name: {activity_name}")

        #with transaction.atomic():
        activity = Activity.objects.create(profile=profile, name=activity_name)
        profile.activity_timer.new_activity(activity)
        profile.activity_timer.refresh_from_db()
        logger.info(f"[CREATE ACTIVITY] Activity '{activity_name}' created for profile {profile.id}. Timer status {profile.activity_timer.status}")

        activity_timer = ActivityTimerSerializer(profile.activity_timer).data
        
        response = {
            "success": True,
            "message": "Activity timer created and ready",
            "activity_timer": activity_timer,
            }
        logger.debug(f"[CREATE ACTIVITY] Response generated for profile {profile.id}: {response}")
        
        return JsonResponse(response)
    
    except json.JSONDecodeError as e:
        logger.error(f"[CREATE ACTIVITY] JSON decode error for profile {profile.id}: {e}")
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        logger.exception(f"[CREATE ACTIVITY] Unexpected error for profile {profile.id}: {e}")
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)


@login_required
#@transaction.atomic
@csrf_exempt
def submit_activity(request):
    """
    Submits the current activity for the logged-in user, awarding XP and resetting timers.

    :param request: The HTTP POST request to submit the activity.
    :type request: django.http.HttpRequest
    :return: A JSON response containing the updated profile, activity rewards, and activities list.
    :rtype: django.http.JsonResponse
    """
    if request.method != "POST":
        logger.warning(f"[SUBMIT ACTIVITY] Invalid method {request.method} used by user {request.user.profile.id}")
        return JsonResponse({"error": "Invalid method"}, status=405)
    
    profile = request.user.profile
    character = PlayerCharacterLink.get_character(profile)

    try:
        logger.info(f"[SUBMIT ACTIVITY] Profile {profile.id} submitting activity")
        logger.debug(f"[SUBMIT ACTIVITY] Activity timer: status {profile.activity_timer.status}, elapsed time {profile.activity_timer.elapsed_time}")
        #with transaction.atomic():
        profile.add_activity(profile.activity_timer.elapsed_time)
        xp_reward = profile.activity_timer.complete()
        profile.activity_timer.refresh_from_db()
        profile.add_xp(xp_reward)

        logger.debug(f"After activity submission and reset: status: {profile.activity_timer.status}, elapsed_time: {profile.activity_timer.elapsed_time}, XP reward: {xp_reward}")

        activities = Activity.objects.filter(profile=profile, created_at__date=timezone.now().date()).order_by('-created_at')
        if not activities.exists():
            activities = Activity.objects.filter(profile=profile).order_by('-created_at')[:5]
            logger.debug(f"[SUBMIT ACTIVITY] No activities for today. Showing recent activities: {activities}")

        activities_list = ActivitySerializer(activities, many=True).data
        profile_serializer = ProfileSerializer(profile).data
        
        response = {
            "success": True,
            "message": "Activity submitted",
            "profile": profile_serializer,
            "activities": activities_list,
            "activity_rewards": xp_reward,
        }
        return JsonResponse(response)
    
    except Exception as e:
        logger.error(f"[SUBMIT ACTIVITY] Error submitting activity for user {profile.id}: {str(e)}", exc_info=True)
        return JsonResponse({"error": "An error occurred while submitting activity"}, status=500)
    

@login_required
@csrf_exempt
def complete_quest(request):
    """
    Completes the currently active quest for the logged-in user's character and processes rewards.

    :param request: The HTTP POST request to complete the quest.
    :type request: django.http.HttpRequest
    :return: A JSON response containing the updated quest list, character info, and timer statuses.
    :rtype: django.http.JsonResponse
    """
    if request.method != "POST":
        logger.warning(f"[COMPLETE QUEST] Invalid method {request.method} used by user {request.user.profile.id}")
        return JsonResponse({"error": "Invalid method"}, status=405)
    
    profile = request.user.profile
    character = PlayerCharacterLink.get_character(profile)
    
    try:
        logger.info(f"[COMPLETE QUEST] Profile {profile.id} initiating quest completion")

        profile.activity_timer.refresh_from_db()
        character.quest_timer.refresh_from_db()

        logger.debug(f"[COMPLETE QUEST] Timers status before: {profile.activity_timer.status}/{character.quest_timer.status}")

        try:
            character.complete_quest()
            #character.quest_timer.refresh_from_db()
            logger.info(f"[COMPLETE QUEST] Quest completed for character {character.id}, timers refreshed.")
        except IntegrityError as e:
            logger.error(f"[COMPLETE QUEST] IntegrityError while completing quest for character {character.id}: {str(e)}", exc_info=True)
        except Exception as e:
            logger.error(f"[COMPLETE QUEST] General error while completing quest for character {character.id}: {str(e)}", exc_info=True)
            raise

        eligible_quests = check_quest_eligibility(character, profile)
        quests = QuestSerializer(eligible_quests, many=True).data
        characterdata = CharacterSerializer(character).data
        
        #logger.debug(f"[COMPLETE QUEST] After quest completion, Activity Timer ID: {id(profile.activity_timer)}, PK: {profile.activity_timer.pk}, Status: {profile.activity_timer.status}")
        logger.debug(f"[COMPLETE QUEST] Timers status after: {profile.activity_timer.status}/{character.quest_timer.status}")

        response = {
            "success": True,
            "message": "Quest completed",
            "xp_reward": 5,
            "quests": quests,
            "character": characterdata,
            'activity_timer_status': profile.activity_timer.status,
            'quest_timer_status': character.quest_timer.status,
        }
        
        return JsonResponse(response)
    
    except Exception as e:
        logger.error(f"[COMPLETE QUEST] Error completing quest for user {profile.id}: {str(e)}", exc_info=True)
        return JsonResponse({"error": "An error occurred while completing quest"}, status=500)


@login_required
@csrf_exempt
def submit_bug_report(request):
    """
    Receives and processes a bug report from the user.

    :param request: The HTTP POST request containing bug report details in JSON format.
    :type request: django.http.HttpRequest
    :return: A JSON response confirming the success or failure of the report submission.
    :rtype: django.http.JsonResponse
    """
    if request.method != "POST":
        logger.warning(f"[SUBMIT BUG REPORT] Invalid method {request.method} used by user {request.user.profile.id}")
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        logger.error(f"Bug Report Received: {data}")
        return JsonResponse({"success": True})

    except Exception as e:
        logger.error(f"Failed to process bug report: {e}", exc_info=True)
        return JsonResponse({"success": False}, status=500)

