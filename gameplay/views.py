from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from .models import Quest, Activity, Character, QuestCompletion, ActivityTimer, QuestTimer
from .serializers import ActivitySerializer, QuestSerializer, CharacterSerializer
from users.serializers import ProfileSerializer
from users.models import Profile
from .utils import check_quest_eligibility
import json
from django.utils.html import escape
from threading import Timer

timers = {}

def stop_timers(profile):
    # Logic to stop the timers
    print(f"Stopping timers for profile {profile.id} due to missed heartbeat")
    activity_timers = ActivityTimer.objects.filter(profile=profile, is_running=True)
    for timer in activity_timers:
        timer.stop()
    
    quest_timers = QuestTimer.objects.filter(character__profile=profile, is_running=True)
    for timer in quest_timers:
        timer.stop()

@login_required
@csrf_exempt
def heartbeat(request):
    if request.method == 'POST':
        profile = request.user.profile
        client_id = profile.id  # Use profile ID as an identifier
        if client_id in timers:
            timers[client_id].cancel()
        timers[client_id] = Timer(10, stop_timers, [profile])  # Stop timers if no heartbeat within 10 seconds
        timers[client_id].start()
        return JsonResponse({'success': True})
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
        return JsonResponse(response)
    return JsonResponse({"error": "Invalid method"}, status=405)

# Fetch quests
@login_required
def fetch_quests(request):
    if request.method == 'GET':
        profile = request.user.profile
        character = Character.objects.get(profile=profile)
        eligible_quests = check_quest_eligibility(character, profile)
        serializer = QuestSerializer(eligible_quests, many=True)
        
        response = {
            "success": True,
            "quests": serializer.data,
            "message": "Eligible quests fetched"
        }
        
        return JsonResponse(response)
    return JsonResponse({"error": "Invalid method"}, status=405)

# Fetch info
@login_required
def fetch_info(request):
    if request.method == "GET":
        profile = request.user.profile
        character = Character.objects.get(profile=profile)
        profile_serializer = ProfileSerializer(profile)
        character_serializer = CharacterSerializer(character)
        current_activity = {"duration": profile.current_activity.duration, "name": profile.current_activity.name} if profile.current_activity else False
        current_quest = QuestSerializer(character.current_quest).data if character.current_quest else False
        return JsonResponse({"success": True, "profile": profile_serializer.data, "character": character_serializer.data, "current_activity": current_activity, "current_quest": current_quest, "message": "Profile and character fetched"})
    return JsonResponse({"error": "Invalid method"}, status=405)

# Choose quest AJAX
@transaction.atomic
@login_required
@csrf_exempt
def choose_quest(request):
    if request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        quest_id = escape(data.get('quest_id'))
        quest = get_object_or_404(Quest, id=quest_id)
        character = Character.objects.get(profile=request.user.profile)
        character.current_quest = quest
        character.save()
        quest_timer, created = QuestTimer.objects.get_or_create(character=character)
        if created:
            quest_timer.duration = quest.duration
        quest_serializer = QuestSerializer(quest)

        response = {
            "success": True,
            "quest": quest_serializer.data,
            "message": f"Quest {quest.name} selected",
        }
        return JsonResponse(response)

    return JsonResponse({"error": "Invalid request"}, status=400)

# Save activity view
@transaction.atomic
@login_required
def save_activity(request):
    if request.method == 'POST':
        activity_name = escape(request.POST['activity'])
        duration = int(request.POST['duration'])
        Activity.objects.create(profile=request.user.profile, name=activity_name, duration=duration)
        return JsonResponse({"success": True, "message": "Activity saved"})
    return JsonResponse({"error": "Invalid method"}, status=405)

@login_required
@transaction.atomic
@csrf_exempt
def create_activity_timer(request):
    if request.method == "POST":
        profile = request.user.profile
        data = json.loads(request.body)
        activity_name = escape(data.get("activityName"))
        if not activity_name:
            return JsonResponse({"error": "Activity name is required"}, status=400)
        activity = profile.current_activity or Activity.objects.create(profile=profile, name=activity_name)
        profile.current_activity = activity
        timer, created = ActivityTimer.objects.get_or_create(profile=profile)
        activity.save()
        timer.save()
        profile.save()

        response = {
            "success": True,
            "message": "Activity timer created and ready",
            }
        return JsonResponse(response)
        
    return JsonResponse({"error": "Invalid method"}, status=405)

@login_required
@csrf_exempt
def start_timer(request):
    if request.method == "POST":
        timer_type = escape(request.body.decode('utf-8'))
        profile = request.user.profile
        timer = ActivityTimer.objects.filter(profile=profile) if timer_type == 'activity' else QuestTimer.objects.filter(character=Character.objects.get(profile=profile))
        if len(timer) == 1:
            timer[0].start()
            return JsonResponse({"success": True, "message": f"{timer_type} timer started"})
        return JsonResponse({"success": False, "message": "Either zero or more than one timer"})
    return JsonResponse({"error": "Invalid method"}, status=405)

@login_required
@csrf_exempt
def stop_timer(request):
    if request.method == "POST":
        timer_type = escape(request.body.decode('utf-8'))
        profile = request.user.profile
        timers = ActivityTimer.objects.filter(profile=profile) if timer_type == 'activity' else QuestTimer.objects.filter(character=Character.objects.get(profile=profile))
        if len(timers) == 1:
            timers[0].stop()
            return JsonResponse({"success": True, "message": f"{timer_type} timer stopped"})
        return JsonResponse({"success": False, "message": f"Error: more than one {timer_type} timer found!"})
    return JsonResponse({"error": "Invalid method"}, status=405)

@login_required
@transaction.atomic
@csrf_exempt
def submit_activity(request):
    if request.method == "POST":
        profile = request.user.profile
        character = Character.objects.get(profile=profile)
        activity = profile.current_activity
        activity_timer = ActivityTimer.objects.get(profile=profile)
        activity_timer.stop()
        print("Activity:", activity.name, "Duration:", activity_timer.elapsed_time)
        activity.add_time(activity_timer.elapsed_time)
        activity_timer.reset()
        QuestTimer.objects.get(character=character).stop()
        rewards = profile.submit_activity()
        activities = Activity.objects.filter(profile=profile, created_at__date=timezone.now().date())
        activities_list = [{"name": act.name, "duration": act.duration, "created_at": act.created_at.isoformat()} for act in activities]
        serializer = ProfileSerializer(profile)
        return JsonResponse({"success": True, "message": "Activity submitted", "profile": serializer.data, "activities": activities_list, "activity_rewards": rewards})
    return JsonResponse({"error": "Invalid method"}, status=405)

@login_required
@transaction.atomic
@csrf_exempt
def quest_completed(request):
    if request.method == "POST":
        profile = request.user.profile
        character = Character.objects.get(profile=profile)
        quest_timer = QuestTimer.objects.get(character=character)
        quest_timer.stop()
        if not quest_timer.is_complete():
            print("Server quest timer says not complete, but quest_completed() fired from client! Remaining time:", quest_timer.get_remaining_time())
        quest_timer.reset()
        ActivityTimer.objects.get(profile=profile).stop()
        character.complete_quest()
        eligible_quests = check_quest_eligibility(character, profile)
        serializer = QuestSerializer(eligible_quests, many=True)
        return JsonResponse({"success": True, "message": "Quest completed", "xp_reward": 5, "eligible_quests": serializer.data})
    return JsonResponse({"error": "Invalid method"}, status=405)

@csrf_exempt
@login_required
def get_timer_state(request):
    if request.method == 'POST':
        timer_type = escape(request.body.decode('utf-8'))
        profile = request.user.profile
        timer = ActivityTimer.objects.filter(profile=profile) if timer_type == 'activity' else QuestTimer.objects.filter(character=Character.objects.get(profile=profile))
        if len(timer) == 1:
            return JsonResponse({"success": True, "timer": {"duration": timer[0].get_elapsed_time()}})
        return JsonResponse({"success": False, "message": "Unexpected item in the baggins area (Either none or too many timers)"})
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