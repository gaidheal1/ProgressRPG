from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import transaction, connection
from django.utils import timezone
from .models import Quest, Activity, QuestCompletion, ActivityTimer, QuestTimer
from character.models import Character, PlayerCharacterLink
from .serializers import ActivitySerializer, QuestSerializer, ActivityTimerSerializer, QuestTimerSerializer
from character.serializers import CharacterSerializer
from users.serializers import ProfileSerializer
from users.models import Profile
from .utils import check_quest_eligibility, start_timers
import json
from django.utils.html import escape
from django.utils.timezone import now

from threading import Timer

timers = {}

HEARTBEAT_TIMEOUT = 20

def stop_heartbeat_timer(client_id):
    if client_id in timers:
        timers[client_id].cancel()
        del timers[client_id]

def start_heartbeat_timer(client_id, profile):
    stop_heartbeat_timer(client_id)
    character = PlayerCharacterLink().get_character(profile)
    character.quest_timer.refresh_from_db()
    print("Starting heartbeat. Quest timer quest:", character.quest_timer.quest)
    
    #print("Now refreshed. Quest timer quest:", character.quest_timer.quest)
    def timeout_callback():
        print(f"timeout callback func")
        stop_heartbeat_timer(client_id)
        if profile.activity_timer.status == 'active':
            stop_timers(profile)

    timers[client_id] = Timer(HEARTBEAT_TIMEOUT, timeout_callback)
    timers[client_id].start()

def stop_timers(profile):
    # Logic to stop the timers
    #if profile.activity_timer.is_active():
    print(f"Stopping timers for profile {profile.name} due to missed heartbeat")
    print("Activity status before pausing:", profile.activity_timer.status)
    profile.activity_timer.pause()
    print("Activity status after pausing:", profile.activity_timer.status)
    character = PlayerCharacterLink().get_character(profile)
    character.quest_timer.pause()

    connection.close()

@login_required
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
        profile = request.user.profile
        #profile.activity_timer.update_activity_time()
        character = PlayerCharacterLink().get_character(profile)
        #character.quest_timer = QuestTimer.objects.get(id=character.quest_timer.id)
        request.session['last_heartbeat'] = timezone.now().timestamp()
        request.session.modified = True
        print(f"Received heartbeat {profile.activity_timer}. {character.quest_timer}")
        start_heartbeat_timer(user_id, request.user.profile)
        #connection.close()
        return JsonResponse({'success': True, 'status': 'ok', 'server_time': now().timestamp()})
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
        connection.close()
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
        connection.close()
        return JsonResponse(response)
    return JsonResponse({"error": "Invalid method"}, status=405)

# Fetch info
@login_required
def fetch_info(request):
    if request.method == "GET":
        profile = request.user.profile
        character = PlayerCharacterLink().get_character(profile)
        print("fetch_info(), character timer:", character.quest_timer)
        profile_serializer = ProfileSerializer(profile).data
        character_serializer = CharacterSerializer(character).data
        current_activity = ActivitySerializer(profile.activity_timer.activity).data if profile.activity_timer.status != 'empty' else False
        current_quest = QuestSerializer(character.quest_timer.quest).data if character.quest_timer.status != 'empty' else False
        quest_elapsed_time = character.quest_timer.elapsed_time if current_quest else 0
        act_timer = ActivityTimerSerializer(profile.activity_timer).data
        quest_timer = QuestTimerSerializer(character.quest_timer).data
        print(act_timer)
        action = start_timers(profile)
        connection.close()
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
        data = json.loads(request.body)
        quest_id = escape(data.get('quest_id'))
        print("choose_quest(), quest_id:", quest_id)
        quest = get_object_or_404(Quest, id=quest_id)
        print("choose_quest(), quest:", quest)
        if quest == None:
            return JsonResponse({"success": False, "message": "Error: quest not found"})
        character = PlayerCharacterLink().get_character(request.user.profile)
        duration = data.get('duration')

        with transaction.atomic():
            character.quest_timer.refresh_from_db()
            character.quest_timer.change_quest(quest, duration) # status should be 'waiting' now
        
        print("change_quest() successful? ", character.quest_timer.quest)
        print(f"{now()} - choose_quest")
        
        action = start_timers(request.user.profile)
        quest_timer = QuestTimerSerializer(character.quest_timer).data
        response = {
            "success": True,
            "quest_timer": quest_timer,
            "message": f"Quest {quest.name} selected",
            "action": action,
        }
        #connection.close()
        print(f"Choose_quest(), just before return: {character.quest_timer}")

        return JsonResponse(response)

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
@transaction.atomic
@csrf_exempt
def create_activity(request):
    if request.method == "POST":
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
        response = {
            "success": True,
            "message": "Activity timer created and ready",
            "activity_timer": activity_timer,
            "action": action,
            }
        connection.close()
        return JsonResponse(response)
        
    return JsonResponse({"error": "Invalid method"}, status=405)

@login_required
@csrf_exempt
def old_start_timers(request):
    if request.method == "POST":
        print("old_start_timers()")
        profile = request.user.profile
        character = PlayerCharacterLink().get_character(profile)
        #print(f"QuestTimer modified: {character.quest_timer.tracker.has_changed('quest')}")
        #print(f"Before save? {character.quest_timer.pk} - {character.quest_timer._state.db} - {character.quest_timer._state.is_modified()}")
        character.quest_timer = QuestTimer.objects.get(id=character.quest_timer.id)
        profile.activity_timer.start()
        character.quest_timer.refresh_from_db()
        print("Before timer start:", character.quest_timer)
        print(f"{now()} - old_start_timers")
        character.quest_timer.start()
        print("After timer start:", character.quest_timer)

        connection.close()
        return JsonResponse({"success": True, "message": "Server timers started"})
    return JsonResponse({"error": "Invalid method"}, status=405)

@login_required
@csrf_exempt
def pause_timers(request):
    if request.method == "POST":
        profile = request.user.profile
        character = PlayerCharacterLink().get_character(profile)
        profile.activity_timer.pause()
        character.quest_timer.pause()

        connection.close()
        return JsonResponse({"success": True, "message": "Server timers paused"})
    return JsonResponse({"error": "Invalid method"}, status=405)

@login_required
@transaction.atomic
@csrf_exempt
def submit_activity(request):
    if request.method == "POST":
        profile = request.user.profile
        character = PlayerCharacterLink().get_character(profile)

        profile.activity_timer.pause()
        character.quest_timer.pause()
        with transaction.atomic():
            profile.activity_timer.refresh_from_db()
            profile.add_activity(profile.activity_timer.elapsed_time)
            xp_reward = profile.activity_timer.complete()
            profile.add_xp(xp_reward)

        activities = Activity.objects.filter(profile=profile, created_at__date=timezone.now().date()).order_by('-created_at')
        if not activities.exists():
            activities = Activity.objects.filter(profile=profile).order_by('-created_at')[:5]
            print("Activities from older days:", activities)
        activities_list = ActivitySerializer(activities, many=True).data
        profile_serializer = ProfileSerializer(profile).data
        
        connection.close()
        return JsonResponse({"success": True, "message": "Activity submitted", "profile": profile_serializer, "activities": activities_list, "activity_rewards": xp_reward})
    return JsonResponse({"error": "Invalid method"}, status=405)

@login_required
@transaction.atomic
@csrf_exempt
def quest_completed(request):
    if request.method == "POST":
        profile = request.user.profile
        character = PlayerCharacterLink().get_character(profile)
        
        profile.activity_timer.refresh_from_db()
        profile.activity_timer.pause()
        print("Activity timer status:", profile.activity_timer.status)
        character.quest_timer.pause()
        print("Quest timer:", character.quest_timer)

        with transaction.atomic():
            character.quest_timer.refresh_from_db()
            character.complete_quest()

        eligible_quests = check_quest_eligibility(character, profile)
        character = CharacterSerializer(character).data
        quests = QuestSerializer(eligible_quests, many=True).data

        connection.close()
        return JsonResponse({"success": True, "message": "Quest completed", "xp_reward": 5, "quests": quests, "character": character})
    return JsonResponse({"error": "Invalid method"}, status=405)

@csrf_exempt
@login_required
def get_timer_state(request):
    if request.method == 'POST':
        profile = request.user.profile
        character = PlayerCharacterLink().get_character(profile)
        activity_time = profile.activity_timer.get_elapsed_time()         
        quest_time = character.quest_timer.get_elapsed_time()
        return JsonResponse({"success": True, "activity_time": activity_time, "quest_time": quest_time})

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