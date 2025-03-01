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

logger = logging.getLogger(__name__)

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
    logger.info(f"[START HEARTBEAT TIMER] reached")
    logger.debug(f"Timer status: {profile.activity_timer.status}/{character.quest_timer.status}")
    
    def timeout_callback():
        logger.info(f"[TIMEOUT CALLBACK] reached")
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
    if request.method == 'POST':
        if request.user.is_authenticated:
            user_id = request.user.profile.id
        else:
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            user_id = f"guest-{session_id}"
        logger.info(f"[HEARTBEAT] Received heartbeat")
        profile = request.user.profile
        character = PlayerCharacterLink().get_character(profile)
        request.session['last_heartbeat'] = timezone.now().timestamp()
        request.session.modified = True
        #logger.debug(f"Timer statuses: {profile.activity_timer.status}/{character.quest_timer.status}")
        #profile.activity_timer.refresh_from_db()
        profile.activity_timer = ActivityTimer.objects.get(pk=profile.activity_timer.pk)
        
        #character.quest_timer.refresh_from_db()
        qt = character.quest_timer
        if qt.status != "completed" and qt.get_remaining_time() <= 0:
            qt.elapsed_time = qt.duration
            stop_timers(profile)
            return JsonResponse({'success': True, 'status': 'quest_complete'})

        print("(heartbeat), Trying id logging:", id(profile.activity_timer))
        logger.debug(f"Heartbeat ID log: id={id(profile.activity_timer)}, pk={profile.activity_timer.pk}, status={profile.activity_timer.status}")
        logger.debug(f"And now after refresh: {profile.activity_timer.status}/{character.quest_timer.status}")
        start_heartbeat_timer(user_id, request.user.profile)
        #for query in connection.queries:
        #    print(query)
        qt = character.quest_timer
        if qt.status != "completed" and qt.get_remaining_time() <= 0:
            stop_timers(profile)
            return JsonResponse({'success': True, 'status': 'quest_complete'})
        #connection.close()
        return JsonResponse({'success': True, 'status': 'ok', 'activity_timer_status': profile.activity_timer.status, 'quest_timer_status': character.quest_timer.status})
    return JsonResponse({"error": "Invalid method"}, status=405)

# Dashboard view
@login_required
def dashboard_view(request):
    profile = request.user.profile
    return render(request, 'gameplay/dashboard.html', {'profile': profile})

# Game view
@transaction.atomic
@login_required
def game_view(request):
    return render(request, 'gameplay/game.html')

# Fetch activities
@login_required
def fetch_activities(request):
    if request.method == 'GET':
        profile = request.user.profile
        activities = Activity.objects.filter(profile=profile, created_at__date=timezone.now().date())
        serializer = ActivitySerializer(activities, many=True)
        
        response = {
            "success": True,
            "activities": serializer.data,
            "message": "Activities fetched"
        }
        #connection.close()
        return JsonResponse(response)
    return JsonResponse({"error": "Invalid method"}, status=405)

# Fetch quests
@login_required
def fetch_quests(request):
    if request.method == 'GET':
        profile = request.user.profile
        character = PlayerCharacterLink().get_character(profile)
        eligible_quests = check_quest_eligibility(character, profile)
        for quest in eligible_quests:
            quest.save()
        serializer = QuestSerializer(eligible_quests, many=True)
        
        response = {
            "success": True,
            "quests": serializer.data,
            "message": "Eligible quests fetched"
        }
        #connection.close()
        return JsonResponse(response)
    return JsonResponse({"error": "Invalid method"}, status=405)

# Fetch info
@login_required
def fetch_info(request):
    if request.method == "GET":
        profile = request.user.profile
        character = PlayerCharacterLink().get_character(profile)
        logger.info(f"[FETCH INFO] reached")
        print(f"Timers:\n{profile.activity_timer}\n{character.quest_timer}")
        profile_serializer = ProfileSerializer(profile).data
        character_serializer = CharacterSerializer(character).data
        current_activity = ActivitySerializer(profile.activity_timer.activity).data if profile.activity_timer.status != 'empty' else False
        current_quest = QuestSerializer(character.quest_timer.quest).data if character.quest_timer.status != 'empty' else False
        quest_elapsed_time = character.quest_timer.elapsed_time if current_quest else 0
        act_timer = ActivityTimerSerializer(profile.activity_timer).data
        quest_timer = QuestTimerSerializer(character.quest_timer).data
        #print(act_timer)
        action = start_timers(profile)
        #print("")
        #connection.close()
        return JsonResponse({"success": True, "profile": profile_serializer, 
            "character": character_serializer, "current_activity": current_activity, 
            "quest": current_quest, "quest_elapsed_time": quest_elapsed_time, 
            "message": "Profile and character fetched", "action": action,
            "activity_timer": act_timer, "quest_timer": quest_timer})
    return JsonResponse({"error": "Invalid method"}, status=405)

# Choose quest
@transaction.atomic
@login_required
@csrf_exempt
def choose_quest(request):
    if request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        logger.info(f"[CHOOSE QUEST] reached")
        data = json.loads(request.body)
        quest_id = escape(data.get('quest_id'))
        #print("choose_quest(), quest_id:", quest_id)
        quest = get_object_or_404(Quest, id=quest_id)
        #print("choose_quest(), quest:", quest)
        if quest == None:
            return JsonResponse({"success": False, "message": "Error: quest not found"})
        character = PlayerCharacterLink().get_character(request.user.profile)
        duration = data.get('duration')

        with transaction.atomic():
            character.quest_timer.change_quest(quest, duration) # status should be 'waiting' now
            character.quest_timer.refresh_from_db()
        
        print("change_quest() successful? ", character.quest_timer.quest)
        
        action = start_timers(request.user.profile)
        logger.debug(f"Action: {action}")
        quest_timer = QuestTimerSerializer(character.quest_timer).data
        response = {
            "success": True,
            "quest_timer": quest_timer,
            "message": f"Quest {quest.name} selected",
            "action": action,
        }
        #connection.close()
        logger.debug(f"Just before return:\n{character.quest_timer}")
        return JsonResponse(response)

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
@transaction.atomic
@csrf_exempt
def create_activity(request):
    if request.method == "POST":
        logger.info(f"[CREATE ACTIVITY] reached")
        profile = request.user.profile
        data = json.loads(request.body)
        activity_name = escape(data.get("activityName"))
        if not activity_name:
            return JsonResponse({"error": "Activity name is required"}, status=400)
        with transaction.atomic():
            activity = Activity.objects.create(profile=profile, name=activity_name)
            profile.activity_timer.new_activity(activity)
        activity_timer = ActivityTimerSerializer(profile.activity_timer).data
        action = start_timers(profile)
        logger.debug(f"Action: {action}")
        response = {
            "success": True,
            "message": "Activity timer created and ready",
            "activity_timer": activity_timer,
            "action": action,
            }
        #connection.close()
        return JsonResponse(response)
        
    return JsonResponse({"error": "Invalid method"}, status=405)


@login_required
@transaction.atomic
@csrf_exempt
def submit_activity(request):
    if request.method == "POST":
        profile = request.user.profile
        character = PlayerCharacterLink().get_character(profile)
        logger.info("[SUBMIT ACTIVITY] reached")

        profile.activity_timer.pause()
        character.quest_timer.pause()

        with transaction.atomic():
            profile.add_activity(profile.activity_timer.elapsed_time)
            xp_reward = profile.activity_timer.complete()
            profile.activity_timer.refresh_from_db()
            profile.add_xp(xp_reward)

        logger.debug(f"After activity submission and reset: status: {profile.activity_timer.status}, elapsed_time: {profile.activity_timer.elapsed_time}")

        activities = Activity.objects.filter(profile=profile, created_at__date=timezone.now().date()).order_by('-created_at')
        if not activities.exists():
            activities = Activity.objects.filter(profile=profile).order_by('-created_at')[:5]
            print("Activities from older days:", activities)

        activities_list = ActivitySerializer(activities, many=True).data
        profile_serializer = ProfileSerializer(profile).data
        
        #connection.close()
        return JsonResponse({"success": True, "message": "Activity submitted", "profile": profile_serializer, "activities": activities_list, "activity_rewards": xp_reward})
    return JsonResponse({"error": "Invalid method"}, status=405)

@login_required
@transaction.atomic
@csrf_exempt
def quest_completed(request):
    if request.method == "POST":
        profile = request.user.profile
        character = PlayerCharacterLink().get_character(profile)
        logger.info(f"[QUEST COMPLETED] reached")
        logger.debug(f"Timers before:\n{profile.activity_timer}\n{character.quest_timer}")
        profile.activity_timer.pause()
        profile.activity_timer.refresh_from_db()
        character.quest_timer.pause()

        try:
            with transaction.atomic():
                character.complete_quest()
                character.quest_timer.refresh_from_db()
        except IntegrityError as e:
            print(f"IntegrityError: {e}")
        except Exception as e:
            print(f"General error: {e}")
            raise

        eligible_quests = check_quest_eligibility(character, profile)
        characterdata = CharacterSerializer(character).data
        quests = QuestSerializer(eligible_quests, many=True).data
        print("(complete quest), Trying id logging:", id(profile.activity_timer))
        logger.debug(f"Complete quest, ID log: id={id(profile.activity_timer)}, pk={profile.activity_timer.pk}, status={profile.activity_timer.status}")

        logger.debug(f"Timers after:\n{profile.activity_timer}\n{character.quest_timer}")

        #for query in connection.queries:
        #    print(query)
        #connection.close()
        
        return JsonResponse({"success": True, "message": "Quest completed", "xp_reward": 5, "quests": quests, "character": characterdata, 'activity_timer_status': profile.activity_timer.status, 'quest_timer_status': character.quest_timer.status})
    return JsonResponse({"error": "Invalid method"}, status=405)

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