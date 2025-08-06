from rest_framework import serializers

from .models import Quest, Activity, QuestResults, ActivityTimer, QuestTimer


class QuestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestResults
        fields = ["dynamic_rewards", "xp_rate", "coin_reward"]


class QuestSerializer(serializers.ModelSerializer):
    result = QuestResultSerializer(source="results", read_only=True)

    class Meta:
        model = Quest
        fields = [
            "id",
            "name",
            "description",
            "intro_text",
            "outro_text",
            "duration_choices",
            "stages",
            "result",
        ]


class ActivitySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Activity
        fields = ["id", "name", "duration", "created_at", "profile"]


class ActivityTimerSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(read_only=True)
    elapsed_time = serializers.SerializerMethodField()

    class Meta:
        model = ActivityTimer
        fields = ["id", "status", "activity", "elapsed_time"]

    def get_elapsed_time(self, obj):
        return obj.get_elapsed_time()


class QuestTimerSerializer(serializers.ModelSerializer):
    quest = QuestSerializer(read_only=True)
    elapsed_time = serializers.SerializerMethodField()
    remaining_time = serializers.SerializerMethodField()

    class Meta:
        model = QuestTimer
        fields = [
            "id",
            "status",
            "quest",
            "duration",
            "elapsed_time",
            "remaining_time",
            "character",
        ]

    def get_elapsed_time(self, obj):
        return obj.get_elapsed_time()

    def get_remaining_time(self, obj):
        return obj.get_remaining_time()
