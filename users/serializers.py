from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'name', 'xp', 'level', 'total_time', 'total_activities', 'is_premium', 'login_streak']
