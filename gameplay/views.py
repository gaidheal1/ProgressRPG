from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Quest, Activity, QuestCompletion, Character, ActivityTimer, QuestTimer
from django.utils import timezone
import json

# Dashboard view
@login_required
def dashboard_view(request):
    profile = request.user.profile
    return render(request, 'gameplay/dashboard.html', {'profile': profile})

# Game view
@login_required
def game_view(request):
    profile = request.user.profile
    activities = Activity.objects.filter(profile=profile) #.order_by('-created_at') # Optional ordering instead of in model
    today = timezone.now().date()
    activities = activities.filter(created_at__date=today)

    character = Character.objects.get(profile=profile)
    char_quests = QuestCompletion.objects.filter(character=character)
    
    quests_done = {}
    for completion in char_quests:
        quests_done[completion.quest] = completion.times_completed
    print(quests_done)
    
    all_quests = Quest.objects.all()

    eligible_quests = []
    for quest in all_quests:
        print('quest:', quest)
        # Test for eligibility
        if quest.checkEligible(character, profile) and \
            quest.not_repeating(character) and \
            quest.requirements_met(quests_done):
            eligible_quests.append(quest)
            print('success')

    print(eligible_quests)
    return render(request, 'gameplay/game.html', 
        {
            'profile': profile,
            'character': character,
            'activities': activities,
            'quests': eligible_quests,
        })

# Choose quest AJAX
@login_required
def choose_quest(request):
    if request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        quest_id = data.get('quest_id')
        
        quest = get_object_or_404(Quest, id=quest_id)
        
        character = Character.objects.get(profile=request.user.profile)
        character.current_quest = quest
        character.save()
        
        quest_timer = ActivityTimer.objects.create(
            character=character,
            duration=quest.duration,
        )
        return JsonResponse({
            "success": True, })

    return JsonResponse({"success": False, "error": "Invalid request"})
        

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


@csrf_exempt
def create_activity_timer(request):
    if request.method == "POST":
        profile = request.user.profile

        data = json.loads(request.body)
        activity_name = data.get("activityName")

        if not activity_name:
            return JsonResponse({"error": "Activity name is required"}, status=400)
        
        # Create activity
        # can I use profile.current_activity?
        activity = Activity.objects.create(
            profile=profile, 
            name=activity_name, 
        )
        timer, created = ActivityTimer.objects.get_or_create(profile=profile)
        
        return JsonResponse({
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
            "activity_id": activity.id,
            })
    return JsonResponse({"error": "Invalid method"}, status=405)


@csrf_exempt
def stop_activity_timer(request):
    profile = request.user.profile
    timer = ActivityTimer.objects.get(profile=profile)
    timer.stop()
    
    return JsonResponse({
        "status": "Activity timer stopped", 
        "elapsed_time": timer.elapsed_time
    })

@csrf_exempt
def submit_activity(request):
    if request.method == "POST":
        profile = request.user.profile
        timer = ActivityTimer.objects.get(profile=profile)
        timer.stop()
    
    return JsonResponse({
        "status": "Activity submitted", 
        "elapsed_time": timer.elapsed_time
    })


@csrf_exempt
def start_quest_timer(request, quest_id):
    character = Character.objects.get(request.user.profile)
    timer, created = QuestTimer.objects.get_or_create(character=character, quest_id=quest_id)
    timer.start()
    return JsonResponse({"status": "Quest timer started"})

@csrf_exempt
def stop_quest_timer(request, quest_id):
    character = Character.objects.get(request.user.profile)
    timer = QuestTimer.objects.get(character=character, quest_id=quest_id)
    timer.stop()
    return JsonResponse({
        "status": "Quest timer stopped", 
        "remaining_time": timer.get_remaining_time(),
    })


@csrf_exempt
def get_timer_state(request):
    profile = request.user.profile
    character = Character.objects.get(request.user.profile)
    activity_timer = ActivityTimer.objects.get(profile=profile)
    quest_timer = QuestTimer.objects.get(character=character)

    response = {
        "activity_timer": {"elapsed_time": activity_timer.elapsed_time},
        "quest_timer": {"remaining_time": quest_timer.get_remaining_time() if quest_timer else None,
        },
    }
    return JsonResponse(response)