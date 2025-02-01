from rest_framework import serializers
from .models import Quest, Activity, Character, QuestResults, Skill, Project


class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = ['id', 'name', 'xp', 'xp_next_level', 'xp_modifier', 'level', 'total_quests']

class QuestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestResults
        fields = ['dynamic_rewards', 'xp_reward', 'coin_reward']

class QuestSerializer(serializers.ModelSerializer):
    result = QuestResultSerializer(source='results', read_only=True)

    class Meta:
        model = Quest
        fields = ['id', 'name', 'description', 'intro_text', 'outro_text', 'duration', 'stages', 'result'] # Add 'stages' field. Will it be able to send it? Should do...

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['id', 'name', 'duration', 'profile', 'created_at']
        read_only_fields = ['created_at']

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'time', 'xp', 'level', 'total_activities', 'last_updated', 'created_at', 'profile']
        read_only_fields = ['last_updated', 'created_at']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'time', 'total_activities', 'last_updated', 'created_at', 'profile']
        read_only_fields = ['last_updated', 'created_at']
