from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import transaction, connection
from django.utils import timezone
from .models import Quest, Activity, QuestCompletion, ActivityTimer, QuestTimer
from character.models import Character, PlayerCharacterLink
from .serializers import ActivitySerializer, QuestSerializer
from character.serializers import CharacterSerializer
from users.serializers import ProfileSerializer
from users.models import Profile
from .utils import check_quest_eligibility
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
    profile.activity_timer.pause()
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
        #profile = request.user.profile
        #profile.activity_timer.update_activity_time()
        #character = PlayerCharacterLink().get_character(profile)
        #character.quest_timer.update_time()
        request.session['last_heartbeat'] = timezone.now().timestamp()
        request.session.modified = True
        
        print(f"Received heartbeat from {user_id}")
        start_heartbeat_timer(user_id, request.user.profile)
        connection.close()
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
        profile_serializer = ProfileSerializer(profile).data
        character_serializer = CharacterSerializer(character).data
        current_activity = ActivitySerializer(profile.activity_timer.activity).data if profile.activity_timer.status != 'empty' else False
        current_quest = QuestSerializer(character.quest_timer.quest).data if character.quest_timer.status != 'empty' else False
        quest_elapsed_time = character.quest_timer.elapsed_time if current_quest else 0
        connection.close()
        return JsonResponse({"success": True, "profile": profile_serializer, 
            "character": character_serializer, "current_activity": current_activity, 
            "quest": current_quest, "quest_elapsed_time": quest_elapsed_time, "message": "Profile and character fetched"})
    return JsonResponse({"error": "Invalid method"}, status=405)

# Choose quest AJAX
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
            character.quest_timer.change_quest(quest, duration)

        print("change_quest() successful? ", character.quest_timer.quest)
        quest_serializer = QuestSerializer(quest)

        response = {
            "success": True,
            "quest": quest_serializer.data,
            "duration": duration,
            "message": f"Quest {quest.name} selected",
        }
        connection.close()
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
        activity = Activity.objects.create(profile=profile, name=activity_name)
        profile.activity_timer.new_activity(activity)
        response = {
            "success": True,
            "message": "Activity timer created and ready",
            }
        connection.close()
        return JsonResponse(response)
        
    return JsonResponse({"error": "Invalid method"}, status=405)

@login_required
@csrf_exempt
def start_timers(request):
    if request.method == "POST":
        profile = request.user.profile
        character = PlayerCharacterLink().get_character(profile)
        profile.activity_timer.start()
        character.quest_timer.start()

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

        profile.activity_timer.pause()
        character.quest_timer.pause()

        print("Character quest timer:", character.quest_timer)
        print("Timer quest:", character.quest_timer.quest)

        with transaction.atomic():
            character.complete_quest(character.quest_timer.quest)
            xp_reward = character.quest_timer.complete() # This resets the quest_timer
            character.add_xp(xp_reward)

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