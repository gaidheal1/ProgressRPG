from django.forms import BaseModelForm
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
import random, json, logging, math
from gameplay.serializers import ActivitySerializer

from .forms import UserRegisterForm, ProfileForm, EmailAuthenticationForm
from .models import Profile
from character.models import Character, PlayerCharacterLink

logger = logging.getLogger("django")

# Index view
def index_view(request):
    return render(request, 'index.html')

# Login view
@transaction.atomic
def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.profile.onboarding_step != 5:
                match user.profile.onboarding_step:
                    case 0 | 1 : return redirect('create_profile')
                    case 2: return redirect('link_character')
                    case 3: return redirect('subscribe')
                    case 4: return redirect('game')
                    case _: raise ValueError("Onboarding step number incorrect")
            return redirect('game')
        else:
            messages.error(request, 'Invalid credentials')
    else:
        if request.user.is_authenticated:
            print("user is logged in already")
            return redirect('game')
        form = EmailAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


# Logout view
def logout_view(request):
    logout(request)
    return redirect('index')


# Register view
class RegisterView(CreateView):
    model = get_user_model()
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('create_profile')

    def form_valid(self, form) -> HttpResponse:
        user = form.save()
        user = authenticate(username=user.username, password=form.cleaned_data['password1'])
        if user is not None:
            login(self.request, user)
        else:
            print('Authentication failed')
        return redirect(self.success_url)
    
# Create profile view
@transaction.atomic
@login_required
def create_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            profile.onboarding_step = 2
            profile.save()
            return redirect('link_character')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'users/create_profile.html', {'form': form})

@transaction.atomic
@login_required
def link_character_view(request):
    if request.method == "POST":
        profile = request.user.profile
        profile.onboarding_step = 3
        profile.save()
        return redirect('subscribe')
    else:
        profile = request.user.profile
        link = PlayerCharacterLink.objects.filter(profile=profile, is_active=True).first()
        character = link.character
    return render(request, 'users/link_character.html', {'random_name': character.name})


# Profile view
@login_required
def profile_view(request):
    profile = request.user.profile
    total_minutes = round(profile.total_time / 60)
    return render(request, 'users/profile.html', {'profile': profile, 'total_minutes': total_minutes})


# Edit profile view
@transaction.atomic
@login_required
def edit_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'users/edit_profile.html', {'form': form})

# Download user data
@transaction.atomic
@login_required
def download_user_data(request):
    user = request.user
    profile = user.profile
    character = Character.objects.get(profile=profile)
    activities_json = ActivitySerializer(profile.activities.all(), many=True).data
    user_data = {
        "username": user.username,
        "email": user.email,
        "profile": {
            "id": profile.id,
            "profile_name": profile.name,
            "level": profile.level,
            "xp": profile.xp,
            "bio": profile.bio,
            "total_time": profile.total_time,
            "total_activities": profile.total_activities,
            "is_premium": profile.is_premium,
        },
        "activities": activities_json,
        "character": {
            "id": character.id,
            "character_name": character.name,
            "level": character.level,
            "total_quests": character.total_quests,
        },
    }

    # Convert to JSON and create a downloadable response
    response = HttpResponse(
        json.dumps(user_data, indent=4), # Pretty-printed JSON
        content_type="application/json"
    )
    response["Content-Disposition"] = 'attachment; filename="user_data.json"'
    return response



@login_required
@transaction.atomic
def delete_account(request):
    if request.method == "POST":
        user = request.user

        logger.info(f"User {user.username} (ID: {user.id}) deleted their account.")

        user.profile.activities.all().delete()
        
        user.profile.delete()

        user.delete()

        request.user.auth_token.delete()
        request.session.flush()
        logout(request)

        return redirect("index")
    else: return render(request, 'users/delete_account.html')