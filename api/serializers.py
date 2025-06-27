from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers


from character.models import Character, PlayerCharacterLink
from gameplay.models import Quest, QuestResults, QuestRequirement, QuestCompletion, Activity, ActivityTimer, QuestTimer
from users.models import Profile, InviteCode



from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
User = get_user_model()



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token

    def validate(self, attrs):
        # Allow login with email instead of username
        attrs['username'] = attrs.get('email')
        return super().validate(attrs)





class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'name', 'xp', 'xp_next_level', 'xp_modifier', 'level', 'total_time', 'total_activities', 'is_premium', 'onboarding_step', 'login_streak']
        read_only_fields = ['id',]


class Step1Serializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['name']

class Step2Serializer(serializers.Serializer):
    # No extra fields for linking character, just confirmation
    confirm_link = serializers.BooleanField()

class Step3Serializer(serializers.Serializer):
    # No extra data, just confirming tutorial completion
    confirm_tutorial = serializers.BooleanField()



class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = ['id', 'first_name', 'sex', 'xp', 'xp_next_level', 'xp_modifier', 'level', 'coins', 'total_quests', 'is_npc', ]
        read_only_fields = ['id',]




class QuestRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestRequirement
        fields = ['prerequisite', 'times_required']

class QuestCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestCompletion
        fields = ['character', 'quest', 'times_completed', 'last_completed']

class QuestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestResults
        fields = ['dynamic_rewards', 'xp_rate', 'coin_reward']


class QuestSerializer(serializers.ModelSerializer):
    results = QuestResultSerializer(read_only=True) # source='results', 

    class Meta:
        model = Quest
        fields = ['id', 'name', 'description', 'intro_text', 'outro_text', 'duration_choices', 'stages', 'results',]
        read_only_fields = ['id',]



class ActivitySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    last_updated = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = Activity
        fields = ['id', 'name', 'duration', 'created_at', 'last_updated', 'profile', 'skill', 'project']
        read_only_fields = ['id', 'created_at', 'last_updated', 'profile']



class ActivityTimerSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(read_only=True)
    elapsed_time = serializers.SerializerMethodField()

    class Meta:
        model = ActivityTimer
        fields = [
            'id', 'status', 'elapsed_time', 'created_at', 'last_updated', # Base timer fields
            'activity', 'profile', # Activity timer specific fields
        ]
        read_only_fields = ['id', 'created_at', 'last_updated', 'profile']

    def get_elapsed_time(self, obj):
        return obj.get_elapsed_time()

class QuestTimerSerializer(serializers.ModelSerializer):
    quest = QuestSerializer(read_only=True)
    elapsed_time = serializers.SerializerMethodField()
    remaining_time = serializers.SerializerMethodField()

    class Meta:
        model = QuestTimer
        fields = [
            'id', 'status',  'elapsed_time', 'created_at', 'last_updated', # Base timer fields
            'quest', 'duration', 'remaining_time', 'character', # Quest timer specific fields
        ]
        read_only_fields = ['id', 'created_at', 'last_updated', 'character', ]

    def get_elapsed_time(self, obj):
        return obj.get_elapsed_time()
    
    def get_remaining_time(self, obj):
        return obj.get_remaining_time()
    
    

class CustomRegisterSerializer(RegisterSerializer):
    invite_code = serializers.CharField(write_only=True, required=True)
    agree_to_terms = serializers.BooleanField(write_only=True, required=True)

    def validate_invite_code(self, value):
        try:
            invite = InviteCode.objects.get(code=value, is_active=True)
        except InviteCode.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired invite code.")
        return value

    def validate_agree_to_terms(self, value):
        if not value:
            raise serializers.ValidationError("You must agree to the terms and conditions.")
        return value
    
    def custom_signup(self, user):
        code = self.validated_data.get("invite_code")
        try:
            invite = InviteCode.objects.get(code=code, is_active=True)
            invite.mark_used(user)
            user.profile.invited_by_code = code
            user.profile.save()
        except InviteCode.DoesNotExist:
            # Should not happen due to earlier validation, but fail safe
            pass
