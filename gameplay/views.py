from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from django.utils.html import escape
from .models import Quest, Activity, Character, QuestCompletion, ActivityTimer, QuestTimer
from .serializers import ActivitySerializer, QuestSerializer, CharacterSerializer
from users.serializers import ProfileSerializer
from users.models import Profile
from .utils import check_quest_eligibility
import json
from django.utils.html import escape
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


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
def start_timer_ws(request):
    if request.method == "POST":
        print("User:", request.user)
        timer_type = escape(request.body.decode('utf-8'))
        profile = request.user.profile
        timer = (
            ActivityTimer.objects.filter(profile=profile) 
            if timer_type == 'activity' 
            else QuestTimer.objects.filter(character=Character.objects.get(profile=profile))
        )

        if not timer:
            return JsonResponse({"success": False, "message": "No timer found"})
        
        timer.start()
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"timer_{profile.id}",
            {
                "type": "timer.start",
                "timer_type": "send_timer_state",
            }
        )

        return JsonResponse({"success": True, "message": f"{timer_type} timer started"})
    
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