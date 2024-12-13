from rest_framework import serializers
from .models import Quest, Activity

class QuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quest
        fields = ['id', 'name', 'description', 'duration', 'xpReward']

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['id', 'name', 'duration', 'profile']