from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.dispatch import receiver
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from .models import Quest, Activity, QuestCompletion, Character, ActivityTimer, QuestTimer
from .serializers import ActivitySerializer, QuestSerializer
from users.serializers import ProfileSerializer
from .utils import check_quest_eligibility
import json

# Dashboard view
@login_required
def dashboard_view(request):
    profile = request.user.profile
    
    #profile.login_streak = 1
    #profile.save()
    
    return render(request, 'gameplay/dashboard.html', {'profile': profile})


# Game view
@transaction.atomic
@login_required
def game_view(request):
    profile = request.user.profile
    
    #profile.login_streak = 1
    #profile.save()
    
    activities = Activity.objects.filter(profile=profile) #.order_by('-created_at') # Optional ordering instead of in model
    today = timezone.now().date()
    activities = activities.filter(created_at__date=today)

    character = Character.objects.get(profile=profile)
    eligible_quests = check_quest_eligibility(character, profile)
    serializer = QuestSerializer(eligible_quests, many=True)
    questsJson = json.dumps(serializer.data)
    # Fetch timers
    activityTimer = ActivityTimer.objects.filter(profile=profile)
    questTimer = QuestTimer.objects.filter(character=character)
    
    if len(questTimer) >= 1:
        questTimer = questTimer[0]

    
    #print(eligible_quests)
    return render(request, 'gameplay/game.html', 
        {
            'profile': profile,
            'character': character,
            'activities': activities,
            
            'questTimer': questTimer,
        })

# Fetch activities
@login_required
def fetch_activities(request):
    profile = request.user.profile
    character = Character.objects.get(profile=profile)

    activities = Activity.objects.filter(profile=profile)
    today = timezone.now().date()
    activities = activities.filter(created_at__date=today)
    serializer = ActivitySerializer(activities, many=True)
    activitiesJson = json.dumps(serializer.data)
    return JsonResponse(activitiesJson, safe=False)


# Fetch quests
@login_required
def fetch_quests(request):
    profile = request.user.profile
    character = Character.objects.get(profile=profile)

    eligible_quests = check_quest_eligibility(character, profile)
    serializer = QuestSerializer(eligible_quests, many=True)
    questsJson = json.dumps(serializer.data)
    return JsonResponse(questsJson, safe=False)


# Choose quest AJAX
@transaction.atomic
@login_required
def choose_quest(request):
    if request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        print("testing invisible choose quests problem")
        data = json.loads(request.body)
        quest_id = data.get('quest_id')
        
        quest = get_object_or_404(Quest, id=quest_id)
        
        character = Character.objects.get(profile=request.user.profile)
        character.current_quest = quest
        character.save()
        
        # One-off:
        #QuestTimer.objects.filter(character=character).delete()
        
        quest_timer, created = QuestTimer.objects.get_or_create(
            character=character,
        )
        if created:
            quest_timer.duration = quest.duration

        print("choose_quest func, quest timer:", quest_timer)


        
        return JsonResponse({
            "success": True,
            "questId": quest.id,
            "questName": quest.name,
            "questDescription": quest.description,
            "questDuration": quest.duration,
            "questStages": quest.stages,
        })

    return JsonResponse({"success": False, "error": "Invalid request"})
        

# Save activity view
@transaction.atomic
@login_required
def save_activity(request):
    if request.method == 'POST':
        activity_name = request.POST['activity']
        duration = int(request.POST['duration'])

        activity = Activity.objects.create(
            profile=request.user.profile, 
            name=activity_name, 
            duration=duration
        )

        return JsonResponse({'status': 'success'})


@transaction.atomic
@csrf_exempt
def create_activity_timer(request):
    if request.method == "POST":
        profile = request.user.profile
        data = json.loads(request.body)
        print(data)
        activity_name = data.get("activityName")

        if not activity_name:
            return JsonResponse({"error": "Activity name is required"}, status=400)
        
        # Create activity
        if profile.current_activity:
            activity = profile.current_activity
            timer, created = ActivityTimer.objects.get_or_create(
                profile=profile,
                activity=activity
            )
            #if created:
             #   timer.activity = activity
        else:
            activity = Activity.objects.create(
                profile=profile, 
                name=activity_name, 
            )
            profile.current_activity = activity
            timer = ActivityTimer.objects.create(
                profile=profile,
                activity=activity,
            )
        print("timer for testing:", timer)
        activity.save()
        timer.save()
        profile.save()
        return JsonResponse({
            "success": True,
            "activity_id": activity.id,
            })
        
    return JsonResponse({"error": "Invalid method"}, status=405)


@csrf_exempt
def start_activity_timer(request):
    if request.method == "POST":
        profile = request.user.profile
        timer = ActivityTimer.objects.get(profile=profile)
        timer.start()
        return JsonResponse({
            "status": "Activity timer started",
            #"activity_id": activity.id,
            })
    return JsonResponse({"error": "Invalid method"}, status=405)


@csrf_exempt
def stop_activity_timer(request):
    if request.method == "POST":
        profile = request.user.profile
        allTimers = ActivityTimer.objects.all()
        
        # This is the problem line. All timers deleted here?
        timer = ActivityTimer.objects.get(profile=profile)
        timer.stop()
        
        return JsonResponse({
            "status": "Activity timer stopped", 
            #"elapsed_time": timer.elapsed_time
        })
    return JsonResponse({"error": "Invalid method"}, status=405)

@transaction.atomic
@csrf_exempt
def submit_activity(request):
    if request.method == "POST":
        print('which comes first? submit activity')
        profile = request.user.profile
        activity = profile.current_activity
        timer = ActivityTimer.objects.get(profile=profile)
        timer.stop()
        
        activity.addTime(timer.elapsed_time)
        
        rewards = profile.submit_activity()

        ActivityTimer.objects.filter(profile=profile).delete()

        activities = Activity.objects.filter(profile=profile)
        today = timezone.now().date()
        activities_list = list(activities.filter(created_at__date=today))
        
        activities_list = [
            {
                "name": act.name,
                "duration": act.duration,
                "created_at": act.created_at.isoformat(),
            }
            for act in activities
        ]
        serializer = ProfileSerializer(profile)
        return JsonResponse({
            "status": "Activity submitted", 
            "profile": serializer.data,
            "activities": activities_list,
            "activity_rewards": rewards,
        })
    return JsonResponse({"error": "Invalid method"}, status=405)


@csrf_exempt
def start_quest_timer(request):
    character = Character.objects.get(profile=request.user.profile)
    timer = QuestTimer.objects.get(character=character)
    timer.start()
    return JsonResponse({"status": "Quest timer started"})

@csrf_exempt
def stop_quest_timer(request):
    character = Character.objects.get(profile=request.user.profile)

    timer = QuestTimer.objects.get(character=character)
    print("quest timer or 404:", timer)
    timer.stop()
    return JsonResponse({
        "status": "Quest timer stopped", 
        "remaining_time": timer.get_remaining_time(),
    })

@transaction.atomic
@csrf_exempt
def quest_completed(request):
    if request.method == "POST":
        profile = request.user.profile
        character = Character.objects.get(profile=profile)
        timer = QuestTimer.objects.get(character=character)
        timer.stop()
        print("quest_completed func, quest timer:", timer)
        # deleteing all quest timers in case extra created accidentally
        QuestTimer.objects.filter(character=character).delete()

        quest = character.current_quest
        character.complete_quest()
        # New quest method: testing!
        #quest.complete()
        
        #quest_results = quest.results
        #print(quest_results)
        eligible_quests = check_quest_eligibility(character, profile)
        serializer = QuestSerializer(eligible_quests, many=True)
        return JsonResponse({
            "status": "Quest completed", 
            "xp_reward": 5,
            "eligible_quests": serializer.data,
        }, safe=False)
    return JsonResponse({"error": "Invalid method"}, status=405)

@csrf_exempt
def get_timer_state(request):
    profile = request.user.profile
    character = Character.objects.get(profile=request.user.profile)
    activity_timer = ActivityTimer.objects.get(profile=profile)
    quest_timer = QuestTimer.objects.get(character=character)

    response = {
        "activity_timer": {"elapsed_time": activity_timer.elapsed_time},
        "quest_timer": {"remaining_time": quest_timer.get_remaining_time() if quest_timer else None,
        },
    }
    return JsonResponse(response)


