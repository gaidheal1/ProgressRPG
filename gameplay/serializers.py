from rest_framework import serializers
from .models import Quest, Activity, QuestResults


class QuestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestResults
        fields = ['dynamic_rewards', 'xp_rate', 'coin_reward']

class QuestSerializer(serializers.ModelSerializer):
    result = QuestResultSerializer(source='results', read_only=True)

    class Meta:
        model = Quest
        fields = ['id', 'name', 'description', 'intro_text', 'outro_text', 'duration_choices', 'stages', 'result']

class ActivitySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = Activity
        fields = ['id', 'name', 'duration', 'created_at', 'profile']

