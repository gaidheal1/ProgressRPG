from rest_framework import serializers
from .models import Quest, Activity, Character


class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = ['id', 'name', 'xp', 'level', 'total_quests']


class QuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quest
        fields = ['id', 'name', 'description', 'duration']

class ActivitySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = Activity
        fields = ['id', 'name', 'duration', 'created_at', 'profile']

