from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from django.utils.html import escape
from .models import Quest, Activity, Character, QuestCompletion, Skill, Project
from .serializers import ActivitySerializer, SkillSerializer, ProjectSerializer, QuestSerializer, CharacterSerializer
from users.serializers import ProfileSerializer
from users.models import Profile
import json
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated



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


class ActivityListCreateView(APIView):
    """ GET all activities, POST new activity """
    #permission_classes = [IsAuthenticated]
    def get(self, request):
        activities = Activity.objects.all() 
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ActivitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() #profile=request.user.profile
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActivityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """ GET, PUT, DELETE for a single acitivty """
    #permission_classes = [IsAuthenticated]
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

    #def get_queryset(self):
    #    return Activity.objects.filter(profile=self.request.user.profile)
    
class SkillListCreateView(APIView):
    """ GET all skills, POST new skill """
    #permission_classes = [IsAuthenticated]
    def get(self, request):
        skills = Skill.objects.all() 
        serializer = SkillSerializer(skills, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = SkillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() #profile=request.user.profile
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    """ GET, PUT, DELETE for a single skill """
    #permission_classes = [IsAuthenticated]
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

    #def get_queryset(self):
    #    return Skill.objects.filter(profile=self.request.user.profile)

class ProjectListCreateView(APIView):
    """ GET all projects, POST new project """
    #permission_classes = [IsAuthenticated]
    def get(self, request):
        projects = Project.objects.all() 
        serializer = ActivitySerializer(projects, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() #profile=request.user.profile
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """ GET, PUT, DELETE for a single project """
    #permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    #def get_queryset(self):
    #    return Project.objects.filter(profile=self.request.user.profile)