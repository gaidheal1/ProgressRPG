from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import transaction, connection, IntegrityError
from django.utils import timezone
from .models import Quest, Activity, QuestCompletion, ActivityTimer, QuestTimer
from character.models import Character, PlayerCharacterLink
from .serializers import ActivitySerializer, QuestSerializer, ActivityTimerSerializer, QuestTimerSerializer
from character.serializers import CharacterSerializer
from users.serializers import ProfileSerializer
from users.models import Profile
from .utils import check_quest_eligibility, start_timers
from django.utils.html import escape
from django.utils.timezone import now
from threading import Timer

import json, logging

logger = logging.getLogger("django")

timers = {}

HEARTBEAT_TIMEOUT = 10

def stop_heartbeat_timer(client_id):
    if client_id in timers:
        timers[client_id].cancel()
        del timers[client_id]

def start_heartbeat_timer(client_id, profile):
    stop_heartbeat_timer(client_id)
    character = PlayerCharacterLink().get_character(profile)
    #character.quest_timer.refresh_from_db()
    logger.info(f"[START HEARTBEAT TIMER] Profile {profile.id} sent heartbeat")
    logger.debug(f"Timers status: {profile.activity_timer.status}/{character.quest_timer.status}")
    
    def timeout_callback():
        logger.info(f"[TIMEOUT CALLBACK] Missed heartbeat from profile {profile.id}")
        logger.debug(f"Timer status: {profile.activity_timer.status}/{character.quest_timer.status}")
        stop_heartbeat_timer(client_id)
        if profile.activity_timer.status == 'active':
            logger.debug("Inside 'if' statement")
            stop_timers(profile)

    timers[client_id] = Timer(HEARTBEAT_TIMEOUT, timeout_callback)
    timers[client_id].start()

def stop_timers(profile):
    # Logic to stop the timers
    #if profile.activity_timer.is_active():
    logger.info(f"[STOP TIMERS] Stopping timers for profile {profile.name} due to missed heartbeat")
    logger.debug(f"Activity status before pausing: {profile.activity_timer.status}")
    profile.activity_timer.pause()
    logger.debug(f"And after pausing: {profile.activity_timer.status}")
    character = PlayerCharacterLink().get_character(profile)
    
    logger.debug(f"Quest status before pausing: {character.quest_timer.status}")
    character.quest_timer.pause()
    logger.debug(f"And after pausing: {character.quest_timer.status}")

    #transaction.on_commit(lambda: logger.debug("Timers committed to DB"))
    #transaction.commit()

@login_required
@transaction.atomic
@csrf_exempt
def heartbeat(request):
    logger.info("[HEARTBEAT] Request received")
    if request.method != 'POST':    
        logger.warning("[HEARTBEAT] Invalid method")
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        if request.user.is_authenticated:
            user_id = request.user.profile.id
        else:
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            user_id = f"guest-{session_id}"

        #logger.debug(f"[HEARTBEAT] User ID: {user_id}")
        
        profile = request.user.profile
        character = PlayerCharacterLink().get_character(profile)

        request.session['last_heartbeat'] = timezone.now().timestamp()
        request.session.modified = True
        
        profile.activity_timer = ActivityTimer.objects.get(pk=profile.activity_timer.pk)
        
        qt = character.quest_timer
        if qt.status != "completed" and qt.get_remaining_time() <= 0:
            logger.info(f"[HEARTBEAT] Quest timer expired for user {user_id}, marking quest as complete")
            qt.elapsed_time = qt.duration
            stop_timers(profile)
            return JsonResponse({'success': True, 'status': 'quest_complete'})

        #logger.debug(f"[HEARTBEAT] Activity Timer: ID={profile.activity_timer.pk}, Status={profile.activity_timer.status}")
        #logger.debug(f"[HEARTBEAT] Quest Timer: ID={qt.pk}, Status={qt.status}")

        start_heartbeat_timer(user_id, request.user.profile)
        
        response = {
            'success': True,
            'status': 'ok',
            'activity_timer_status': profile.activity_timer.status,
            'quest_timer_status': character.quest_timer.status,
        }
        return JsonResponse(response)
    
    except Exception as e:
        logger.error(f"[HEARTBEAT] Error processing heartbeat for user {user_id}: {str(e)}", exc_info=True)
        return JsonResponse({"error": "An error occurred"}, status=500)


# Dashboard view
@login_required
def dashboard_view(request):
    profile = request.user.profile
    return render(request, 'gameplay/dashboard.html', {'profile': profile})

# Game view
@transaction.atomic
@login_required
def game_view(request):
    try:
        logger.info(f"[GAME VIEW] Accessed by user {request.user.profile.id}")
        return render(request, 'gameplay/game.html')
    except Exception as e:
        logger.error(f"[GAME VIEW] Error rendering game view for user {request.user.profile.id}: {str(e)}", exc_info=True)
        return JsonResponse({"error": "An error occurred"}, status=500)

# Fetch activities
@login_required
def fetch_activities(request):
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
    if request.method != 'GET':
        logger.warning(f"[FETCH QUESTS] Invalid method {request.method} used by user {request.user.profile.id}")
        return JsonResponse({"error": "Invalid method"}, status=405)

    profile = request.user.profile
    logger.info(f"[FETCH QUESTS] Request received from user {profile.id}")
    character = PlayerCharacterLink().get_character(profile)

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

    
# Fetch info
@login_required
def fetch_info(request):
    if request.method != "GET":
        logger.warning(f"[FETCH INFO] Invalid method {request.method} used by user {request.user.profile.id}")
        return JsonResponse({"error": "Invalid method"}, status=405)
    
    profile = request.user.profile
    character = PlayerCharacterLink().get_character(profile)
    try:
        logger.info(f"[FETCH INFO] Fetching data for profile {profile.id}, character {character.id}")

        logger.debug(f"[FETCH INFO] Timers status: {profile.activity_timer.status}/{character.quest_timer.status}")

        profile_serializer = ProfileSerializer(profile).data
        character_serializer = CharacterSerializer(character).data

        act_timer = ActivityTimerSerializer(profile.activity_timer).data
        quest_timer = QuestTimerSerializer(character.quest_timer).data
        
        action = start_timers(profile)
        if action:
            logger.info(f"[FETCH INFO] Timers started for profile {profile.id}: {action}")

        response = {
            "success": True,
            "profile": profile_serializer,
            "character": character_serializer,
            "message": "Profile and character fetched",
            "activity_timer": act_timer,
            "quest_timer": quest_timer,
            "action": action,
        }

        logger.debug(f"[FETCH INFO] Response generated successfully for profile {profile.id}")

        return JsonResponse(response)
    
    except Exception as e:
        logger.error(f"[FETCH INFO] Error fetching info for user {profile.id}: {str(e)}", exc_info=True)
        return JsonResponse({"error": "An error occurred while fetching info"}, status=500)
    

# Choose quest
@transaction.atomic
@login_required
@csrf_exempt
def choose_quest(request):
    if request.method != "POST":
        logger.warning(f"[CHOOSE QUEST] Invalid method {request.method} used by user {request.user.profile.id}")
        return JsonResponse({"error": "Invalid request"}, status=400)
    
    if request.headers.get('Content-Type') != 'application/json':
        logger.warning(f"[CHOOSE QUEST] Invalid content type: {request.headers.get('Content-Type')}")
        return JsonResponse({"error": "Invalid content type"}, status=400)
        
    try:
        logger.info(f"[CHOOSE QUEST] User {request.user.profile.id} initiated quest selection")
        data = json.loads(request.body)
        quest_id = escape(data.get('quest_id'))
        quest = get_object_or_404(Quest, id=quest_id)
        
        if not quest:
            logger.warning(f"[CHOOSE QUEST] Quest ID {quest_id} not found for user {request.user.profile.id}")
            return JsonResponse({"success": False, "message": "Error: quest not found"})
        
        character = PlayerCharacterLink().get_character(request.user.profile)
        duration = data.get('duration')

        with transaction.atomic():
            character.quest_timer.change_quest(quest, duration) # status should be 'waiting' now
            character.quest_timer.refresh_from_db()
        
        logger.info(f"[CHOOSE QUEST] Quest {quest.name} (ID: {quest.id}) selected by user {request.user.profile.id}")
        
        action = start_timers(request.user.profile)
        if action:
            logger.info(f"[CHOOSE QUEST] Timers started for user {request.user.profile.id}: {action}")

        quest_timer = QuestTimerSerializer(character.quest_timer).data
        response = {
            "success": True,
            "quest_timer": quest_timer,
            "message": f"Quest {quest.name} selected",
            "action": action,
        }
        
        logger.debug(f"[CHOOSE QUEST] Response generated successfully for user {request.user.profile.id}")
        
        return JsonResponse(response)

    except json.JSONDecodeError as e:
        logger.error(f"[CHOOSE QUEST] JSON decode error for user {request.user.profile.id}: {e}")
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        logger.exception(f"[CHOOSE QUEST] Unexpected error for user {request.user.profile.id}: {e}")
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)
    

@login_required
@transaction.atomic
@csrf_exempt
def create_activity(request):
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

        with transaction.atomic():
            activity = Activity.objects.create(profile=profile, name=activity_name)
            profile.activity_timer.new_activity(activity)
        
        logger.info(f"[CREATE ACTIVITY] Activity '{activity_name}' created for profile {profile.id}")

        activity_timer = ActivityTimerSerializer(profile.activity_timer).data
        
        action = start_timers(profile)
        if action:
            logger.info(f"[CHOOSE QUEST] Timers started for user {request.user.profile.id}: {action}")
        
        response = {
            "success": True,
            "message": "Activity timer created and ready",
            "activity_timer": activity_timer,
            "action": action,
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
@transaction.atomic
@csrf_exempt
def submit_activity(request):
    if request.method != "POST":
        logger.warning(f"[SUBMIT ACTIVITY] Invalid method {request.method} used by user {request.user.profile.id}")
        return JsonResponse({"error": "Invalid method"}, status=405)
    
    profile = request.user.profile
    character = PlayerCharacterLink().get_character(profile)

    try:
        logger.info(f"[SUBMIT ACTIVITY] Profile {profile.id} submitting activity")

        profile.activity_timer.pause()
        character.quest_timer.pause()
        logger.debug(f"[SUBMIT ACTIVITY] Timers paused: activity_timer status = {profile.activity_timer.status}, quest_timer status = {character.quest_timer.status}")

        with transaction.atomic():
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
@transaction.atomic
@csrf_exempt
def quest_completed(request):
    if request.method != "POST":
        logger.warning(f"[QUEST COMPLETED] Invalid method {request.method} used by user {request.user.profile.id}")
        return JsonResponse({"error": "Invalid method"}, status=405)
    
    profile = request.user.profile
    character = PlayerCharacterLink().get_character(profile)
    
    try:
        logger.info(f"[QUEST COMPLETED] Profile {profile.id} initiating quest completion")
        logger.debug(f"[QUEST COMPLETED] Timers status before: {profile.activity_timer.status}/{character.quest_timer.status}")

        profile.activity_timer.pause()
        profile.activity_timer.refresh_from_db()
        character.quest_timer.pause()

        try:
            with transaction.atomic():
                character.complete_quest()
                character.quest_timer.refresh_from_db()
                logger.info(f"[QUEST COMPLETED] Quest completed for character {character.id}, timers refreshed.")
        except IntegrityError as e:
            logger.error(f"[QUEST COMPLETED] IntegrityError while completing quest for character {character.id}: {str(e)}", exc_info=True)
        except Exception as e:
            logger.error(f"[QUEST COMPLETED] General error while completing quest for character {character.id}: {str(e)}", exc_info=True)
            raise

        eligible_quests = check_quest_eligibility(character, profile)
        characterdata = CharacterSerializer(character).data
        quests = QuestSerializer(eligible_quests, many=True).data
        
        logger.debug(f"[QUEST COMPLETED] After quest completion, Activity Timer ID: {id(profile.activity_timer)}, PK: {profile.activity_timer.pk}, Status: {profile.activity_timer.status}")
        logger.debug(f"[QUEST COMPLETED] Timers status after: {profile.activity_timer.status}/{character.quest_timer.status}")

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
        logger.error(f"[QUEST COMPLETED] Error completing quest for user {profile.id}: {str(e)}", exc_info=True)
        return JsonResponse({"error": "An error occurred while completing quest"}, status=500)







@login_required
def get_game_statistics(request):
    if request.method == 'GET':
        profiles = Profile.objects.all()
        profiles_num = len(profiles)
        highest_login_streak_ever = max(profile.login_streak_max for profile in profiles)
        highest_login_streak_current = max(profile.login_streak for profile in profiles)
        activities = Activity.objects.all()
        total_activity_num = len(activities)
        total_activity_time = sum(activity.duration for activity in activities)
        activities_num_average = total_activity_num / profiles_num
        activities_time_average = total_activity_time / profiles_num
        characters = Character.objects.all()
        characters_num = len(characters)
        questsCompleted = QuestCompletion.objects.all()
        unique_quests = set(qc.quest for qc in questsCompleted)
        total_quests = sum(qc.times_completed for qc in questsCompleted)
        quests_num_average = total_quests / characters_num
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Invalid method"}, status=405)