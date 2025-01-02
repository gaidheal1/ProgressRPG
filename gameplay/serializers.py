from rest_framework import serializers
from .models import Quest, Activity, Character


class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = ['id', 'name', 'xp', 'xp_next_level', 'xp_modifier', 'level', 'total_quests']


class QuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quest
        fields = ['id', 'name', 'description', 'duration', 'stages'] # Add 'stages' field. Will it be able to send it? Should do...

class ActivitySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = Activity
        fields = ['id', 'name', 'duration', 'created_at', 'profile']

