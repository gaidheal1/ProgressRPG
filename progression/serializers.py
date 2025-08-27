from rest_framework import serializers

from .models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Activity
        fields = ["id", "name", "duration", "created_at", "profile"]
