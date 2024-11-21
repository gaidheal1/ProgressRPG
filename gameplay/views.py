from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Quest, Activity

# Dashboard view
@login_required
def dashboard_view(request):
    return render(request, 'gameplay/dashboard.html')

# Game view
@login_required
def game_view(request):
    return render(request, 'gameplay/game.html')


@login_required
def save_activity(request):
    if request.method == 'POST':
        activity_name = request.POST['activity']
        duration = int(request.POST['duration'])
        quest_id = request.POST['quest_id']

        activity = Activity.objects.create(
            name=activity_name, duration=duration, user=request.user, quest_id=quest_id
        )

        return JsonResponse({'status': 'success'})
