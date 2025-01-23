from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.dispatch import receiver
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from .models import Quest, Activity, QuestCompletion, Character, ActivityTimer, QuestTimer
from .serializers import ActivitySerializer, QuestSerializer, CharacterSerializer
from users.serializers import ProfileSerializer
from users.models import Profile
from .utils import check_quest_eligibility
import json
# Was trying to create a graph of objects but need to install these packages first
#import matplotlib.pyplot as plt
#import pandas as pd

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
    
    #activities = Activity.objects.filter(profile=profile) #.order_by('-created_at') # Optional ordering instead of in model
    #today = timezone.now().date()
    #activities = activities.filter(created_at__date=today)

    character = Character.objects.get(profile=profile)
    #eligible_quests = check_quest_eligibility(character, profile)
    #serializer = QuestSerializer(eligible_quests, many=True)
    #questsJson = json.dumps(serializer.data)
    # Fetch timers
    #activityTimer = ActivityTimer.objects.filter(profile=profile)
    #questTimer = QuestTimer.objects.filter(character=character)
    
    #if len(questTimer) >= 1:
    #    questTimer = questTimer[0]

    #print(eligible_quests)
    return render(request, 'gameplay/game.html') # removed the dictionary as now using AJAX request to load data separately.


# Fetch activities
@login_required
def fetch_activities(request):
    if request.method == 'GET':
        profile = request.user.profile
        character = Character.objects.get(profile=profile)

        activities = Activity.objects.filter(profile=profile)
        today = timezone.now().date()
        activities = activities.filter(created_at__date=today)
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
        print(response)
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

        if profile.current_activity:
            current_activity = {
                "duration": profile.current_activity.duration,
                "name": profile.current_activity.name,
            }
        else: current_activity = False

        if character.current_quest:
            #current_quest = {
            #    "duration": profile.current_activity.duration,
            #    "name": profile.current_activity.name,
            #}
            current_quest = QuestSerializer(character.current_quest)
            current_quest = current_quest.data
        else: current_quest = False
        response = {
            "success": True,
            "profile": profile_serializer.data,
            "character": character_serializer.data,
            "current_activity": current_activity,
            "current_quest": current_quest,
            "message": "Profile and character fetched"
        }
        return JsonResponse(response)
    return JsonResponse({"error": "Invalid method"}, status=405)


# Choose quest AJAX
@transaction.atomic
@login_required
@csrf_exempt
def choose_quest(request):
    if request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        quest_id = data.get('quest_id')
        
        quest = get_object_or_404(Quest, id=quest_id)
        
        character = Character.objects.get(profile=request.user.profile)
        character.current_quest = quest
        character.save()
        
        # One-off for deleting any extra Quest Timers if necessary
        #QuestTimer.objects.filter(character=character).delete()
        
        quest_timer, created = QuestTimer.objects.get_or_create(
            character=character,
        )
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
        activity_name = request.POST['activity']
        duration = int(request.POST['duration'])

        activity = Activity.objects.create(
            profile=request.user.profile, 
            name=activity_name, 
            duration=duration
        )

        response = {
            "success": True,
            "message": "Activity saved",
        }
        return JsonResponse(response)
    return JsonResponse({"error": "Invalid method"}, status=405)

@login_required
@transaction.atomic
@csrf_exempt
def create_activity_timer(request):
    if request.method == "POST":
        profile = request.user.profile
        data = json.loads(request.body)
        #print(data)
        activity_name = data.get("activityName")

        if not activity_name:
            return JsonResponse({"error": "Activity name is required"}, status=400)

        # One-off delete if necessary
        #ActivityTimer.objects.filter(profile=profile).delete()

        # Create activity
        if profile.current_activity:
            profile.current_activity.name = activity_name
            activity = profile.current_activity
        else:
            activity = Activity.objects.create(
                profile=profile, 
                name=activity_name,
            )
            profile.current_activity = activity
        timer, created = ActivityTimer.objects.get_or_create(
                profile=profile,
        )
        #print("timer for testing:", timer)
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
        timer_type = request.body.decode('utf-8')
        profile = request.user.profile
        print("start_timer func, timer_type:", timer_type)
        if timer_type == 'activity':
            timer = ActivityTimer.objects.filter(profile=profile)
            
        elif timer_type == 'quest':
            character = Character.objects.get(profile=profile)
            timer = QuestTimer.objects.filter(character=character)
        else: 
            response = {
                "success": False,
                "message": "Error: Unknown timer type"
                }

        if len(timer) == 1:
            response = {
                "success": True,
                "message": f"{timer_type} timer started"
                }
            timer[0].start()
        else:
            # If response not already generated with error
            if response == False:
                response = {
                    "success": False,
                    "message": "Either zero or more than one timer"
                    }    

        return JsonResponse(response)
    return JsonResponse({"error": "Invalid method"}, status=405)

@login_required
@csrf_exempt
def stop_timer(request):
    if request.method == "POST":

        timer_type = request.body.decode('utf-8')
        profile = request.user.profile

        if timer_type == 'activity':
            timers = ActivityTimer.objects.filter(profile=profile)
        elif timer_type == 'quest':
            character = Character.objects.get(profile=profile)
            timers = QuestTimer.objects.filter(character=character)
        else: 
            response = {
                "success": False,
                "message": "Error: Unknown timer type",
                }

        if len(timers) == 1:
            response = {
                "success": True,
                "message": f"{timer_type} timer stopped",
                }
            timers[0].stop()
        else: 
            response = {
                "success": False,
                "message": f"Error: more than one {timer_type} timer found!",
            }
        return JsonResponse(response)
    return JsonResponse({"error": "Invalid method"}, status=405)

@login_required
@transaction.atomic
@csrf_exempt
def submit_activity(request):
    if request.method == "POST":
        #print('which comes first? submit activity')
        profile = request.user.profile
        character = Character.objects.get(profile=profile)

        activity = profile.current_activity

        activity_timer = ActivityTimer.objects.get(profile=profile)
        activity_timer.stop()
        activity.add_time(activity_timer.elapsed_time)
        activity_timer.reset()
        quest_timer = QuestTimer.objects.get(character=character)
        quest_timer.stop()
        
        rewards = profile.submit_activity()
        
        #ActivityTimer.objects.filter(profile=profile).delete()

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

        response = {
            "success": True,
            "message": "Activity submitted", 
            "profile": serializer.data,
            "activities": activities_list,
            "activity_rewards": rewards,
        }
        return JsonResponse(response)
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
        if not quest_timer.is_complete(): print("Server quest timer says not complete, but quest_completed() fired from client! Remaining time:", quest_timer.get_remaining_time())
        quest_timer.reset()

        activity_timer = ActivityTimer.objects.get(profile=profile)
        activity_timer.stop()
	# Not sure I need the next line. Unless I subtract the elapsed time from the timer I'm just doubling up, I think
        #activity.add_time(timer.elapsed_time)

        #print("quest_completed func, quest timer:", timer)
        # No longer deleting Quest timer object
        # May need to check if multiple timers being created and delete all but one
        #QuestTimer.objects.filter(character=character).delete()

        quest = character.current_quest
        character.complete_quest()
        # New quest method: testing!
        #quest.complete()
        
        #quest_results = quest.results
        #print(quest_results)
        eligible_quests = check_quest_eligibility(character, profile)
        serializer = QuestSerializer(eligible_quests, many=True)

        response = {
            "success": True,
            "message": "Quest completed", 
            "xp_reward": 5,
            "eligible_quests": serializer.data,
        }
        return JsonResponse(response)
    return JsonResponse({"error": "Invalid method"}, status=405)

@csrf_exempt
@login_required
def get_timer_state(request):
    if request.method == 'POST': 
        timer_type = request.body.decode('utf-8')  # Decode the plain text body
        print("Received timer:", timer_type)

        profile = request.user.profile
        response = {}
        if timer_type == 'activity':
            timer = ActivityTimer.objects.filter(profile=profile)
        
        elif timer_type == 'quest':
            character = Character.objects.get(profile=profile)
            timer = QuestTimer.objects.filter(character=character)
        else: 
            response = {
                "success": False,
                "message": "Unknown timer type"
                }
        print("get_timer_state func, timer:", timer)
        if len(timer) == 1:
            response = {
                "success": True,
                "timer": {"duration": timer[0].get_elapsed_time()},
                }
        else:
            if not response:
                response = {
                    "success": False,
                    "message": "Unexpected item in the baggins area (Either none or too many timers)"
                    }
        return JsonResponse(response)
    return JsonResponse({"error": "Invalid method"}, status=405)


@login_required
def get_game_statistics(request):
    if request.method == 'GET':

        profiles = Profile.objects.all()
        profiles_num = len(profiles)
        highest_login_streak_ever = 0
        highest_login_streak_current = 0
        for profile in profiles:
            if highest_login_streak_ever < profile.login_streak_max:
                highest_login_streak_ever = profile.login_streak_max
            if highest_login_streak_current < profile.login_streak:
                highest_login_streak_current = profile.login_streak

        print(f"login streaks. current high: {highest_login_streak_current}, max high: {highest_login_streak_ever}")
        activities = Activity.objects.all()
        total_activity_num = len(activities)
        total_activity_time = 0
        for activity in activities:
            total_activity_time += activity.duration
        
        # Total activities completed by players: total_activity_num
        # Total activity time logged by players: total_activity_time
        #print("activity num and time:", total_activity_num, total_activity_time)
        
        activities_num_average = total_activity_num / profiles_num
        activities_time_average = total_activity_time / profiles_num
        #print(f"activities per player: {activities_num_average}; time per player: {activities_time_average}")

        activities_json = ActivitySerializer(activities, many=True)
        
        # To add later when characters more advanced:
        # 
        #characters = Character.objects.all()
        #characters_num = len(characters)

        questsCompleted = QuestCompletion.objects.all()
        unique_quests = set()
        total_quests = 0
        for qc in questsCompleted:
            unique_quests.add(qc.quest)
            total_quests += qc.times_completed

        quests_num_average = total_quests / characters_num
        #print(f"num of characters: {characters_num}; quests per character: {quests_num_average}")
        # Unique quests completed: len(unique_quests)
        # Total quests completed: total_quests
        #print(f"unique quests completed: {len(unique_quests)}, total quests completed: {total_quests}")
        
        def create_timeseries_graph(objects, datetime_field, timescale='daily'):
            df = pd.DataFrame([getattr(obj, datetime_field) for obj in objects], columns=[datetime_field])

            df[datetime_field] = pd.to_datetime(df[datetime_field])

            if timescale == 'daily':
                df_resampled = df.resample('D', on=datetime_field).count()

            fig, ax = plt.subplots()
            df_resampled.plot(ax=ax)
            ax.set_xlabel(f"Time ({timescale})")
            ax.set_ylabel("Count")
            ax.set_title(f"Object count by {timescale}")
            return fig

        #fig = create_timeseries_graph(activities, 'created_at')
        #plt.show()

        response = {
            "success": True,
        }
        return JsonResponse(response)