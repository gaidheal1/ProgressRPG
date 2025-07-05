# api/views.py
from asgiref.sync import async_to_sync
from datetime import datetime
from django.conf import settings
from django.contrib.auth import login, logout, get_user_model
from django.core.mail import send_mail
from django.db import DatabaseError, transaction
from django.http import Http404  # , HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit

from allauth.account import app_settings as allauth_settings
from allauth.account.models import EmailConfirmationHMAC
from allauth.account.utils import complete_signup
from dj_rest_auth.registration.views import RegisterView

from rest_framework import viewsets, permissions, serializers, status, mixins
from rest_framework.decorators import (
    api_view,
    permission_classes,
    action,
    authentication_classes,
)
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView

# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from api.serializers import (
    UserSerializer,
    ProfileSerializer,
    CharacterSerializer,
    ActivitySerializer,
    QuestSerializer,
    ActivityTimerSerializer,
    QuestTimerSerializer,
    Step1Serializer,
    # Step2Serializer,
    # Step3Serializer,
    CustomTokenObtainPairSerializer,
)

from character.models import Character, PlayerCharacterLink
from gameplay.models import Activity, Quest, ActivityTimer, QuestTimer, ServerMessage
from gameplay.utils import check_quest_eligibility, send_group_message
from users.models import Profile

import logging

logger = logging.getLogger("django")


class IsOwnerProfile(permissions.BasePermission):
    owner_attr = "profile"

    def has_object_permission(self, request, view, obj):
        profile = getattr(request.user, "profile", None)
        if profile is None:
            return False

        # Check if object has 'profile' attribute and compare
        if hasattr(obj, "profile"):
            return obj.profile == profile

        return False


class IsOwnerCharacter(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        profile = getattr(request.user, "profile", None)
        if profile is None:
            return False

        # Check if the object's character is linked to the profile and active
        if hasattr(obj, "character"):
            return PlayerCharacterLink.objects.filter(
                profile=profile, character=obj.character, is_active=True
            ).exists()

        return False


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @csrf_exempt
    @api_view(["POST"])
    def test_post_view(request):
        permission_classes = [IsAuthenticated]
        return Response(
            {"status": "ok", "message": f"Hello {request.user.email}! POST successful!"}
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


class CustomRegisterView(RegisterView):
    def perform_create(self, serializer):
        user = serializer.save(self.request)

        backend_path = settings.AUTHENTICATION_BACKENDS[0]
        user.backend = backend_path

        # Complete signup (this triggers login)
        complete_signup(self.request, user, allauth_settings.EMAIL_VERIFICATION, None)
        return user

    def get_response_data(self, user):
        # Override to avoid Token and return JWT tokens instead

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


def confirm_email_and_redirect(request, key):
    try:
        confirmation = EmailConfirmationHMAC.from_key(key)
        if not confirmation:
            raise Http404("Invalid or expired confirmation key")

        # Confirm the email
        confirmation.confirm(request)
        user = confirmation.email_address.user

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        return Response(
            {
                "message": "Email confirmed",
                "access": access,
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )

    except Exception:
        raise Http404("Invalid confirmation link")


class ProfileViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Restrict access to only the logged-in user's profile
        return Profile.objects.filter(user=self.request.user)


class OnboardingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_profile(self, request):
        return request.user.profile

    @action(detail=False, methods=["post"])
    def progress(self, request):
        profile = self.get_profile(request)
        step = profile.onboarding_step

        if step == 1:
            serializer = Step1Serializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                profile.onboarding_step = 2
                profile.save()
                return Response(
                    {
                        "message": "Profile updated and onboarding step set to 2.",
                        "step": 2,
                    }
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif step == 2:
            link = PlayerCharacterLink.objects.filter(
                profile=profile, is_active=True
            ).first()
            if not link:
                return Response(
                    {"error": "No active character link found."}, status=404
                )

            profile.onboarding_step = 3
            profile.save()
            return Response({"message": "Character confirmed", "step": 3})

        elif step == 3:
            profile.onboarding_step = 4
            profile.save()
            return Response({"message": "Tutorial complete", "step": 4})

        else:
            return Response(
                {"message": "Onboarding complete."}, status=status.HTTP_200_OK
            )


class FetchInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        profile = request.user.profile
        try:
            character = PlayerCharacterLink.get_character(profile)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        logger.info(
            f"[FETCH INFO] Fetching data for profile {profile.id}, character {character.id}"
        )
        logger.debug(
            f"[FETCH INFO] Timers status: {profile.activity_timer.status}/{character.quest_timer.status}"
        )

        qt = character.quest_timer
        if qt.time_finished() and qt.status != "completed":
            try:
                qt.elapsed_time = qt.duration
                qt.save()
                async_to_sync(send_group_message)(
                    f"profile_{profile.id}",
                    {"type": "action", "action": "quest_complete"},
                )
            except Exception as e:
                logger.error(f"Error handling quest timer completion: {e}")
                return Response(
                    {
                        "error": "An error occurred while handling quest timer completion."
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        if (
            profile.activity_timer.status != "empty"
            and profile.activity_timer.activity is None
        ):
            try:
                profile.activity_timer.reset()
            except Exception as e:
                logger.error(f"Error resetting activity timer: {e}")
                return Response(
                    {"error": "An error occurred while resetting the activity timer."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        try:
            profile_data = ProfileSerializer(profile, context={"request": request}).data
            character_data = CharacterSerializer(
                character, context={"request": request}
            ).data
            activity_timer_data = ActivityTimerSerializer(
                profile.activity_timer, context={"request": request}
            ).data
            quest_timer_data = QuestTimerSerializer(
                qt, context={"request": request}
            ).data

            return Response(
                {
                    "success": True,
                    "profile": profile_data,
                    "character": character_data,
                    "message": "Profile and character fetched",
                    "activity_timer": activity_timer_data,
                    "quest_timer": quest_timer_data,
                }
            )

        except Exception as e:
            logger.error(f"Serialization error: {e}")
            return Response(
                {"error": "An error occurred during serialization."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CharacterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for listing and retrieving characters.
    Characters can be browsed by authenticated users — for example,
    to view their history or find nearby players.

    Modifications to characters should happen only via gameplay endpoints
    (e.g. quest completion, XP gain), not through direct update.
    """

    serializer_class = CharacterSerializer
    permission_classes = [IsAuthenticated]
    queryset = Character.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Example: later you might filter by proximity or visibility
        # location = user.profile.location
        # queryset = queryset.filter(location__near=location)

        return queryset


class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated, IsOwnerProfile]

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)

    def get_queryset(self):
        profile = self.request.user.profile
        queryset = Activity.objects.filter(profile=profile)

        # Check if a 'date' query param is provided, e.g. ?date=2025-06-25
        date_str = self.request.query_params.get("date")
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                queryset = queryset.filter(created_at__date=date_obj)
            except ValueError:
                pass  # Invalid date format, just ignore filtering by date

        return queryset.order_by("-created_at")

    def create(self, request, *args, **kwargs):
        profile = request.user.profile
        activity_name_raw = request.data.get("activityName")

        if not activity_name_raw:
            return Response(
                {"error": "Activity name is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        activity_name = escape(activity_name_raw)

        try:
            activity = Activity.objects.create(profile=profile, name=activity_name)
            profile.activity_timer.new_activity(activity)
            profile.activity_timer.refresh_from_db()
        except DatabaseError:
            return Response(
                {"error": "A database error occurred while creating the activity."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            activity_timer_data = ActivityTimerSerializer(
                profile.activity_timer, context={"request": request}
            ).data
        except ValidationError:
            return Response(
                {"error": "Invalid data encountered during serialization."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "success": True,
                "message": "Activity timer created and ready",
                "activity_timer": activity_timer_data,
            }
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="submit",
        permission_classes=[IsAuthenticated],
    )
    def submit(self, request, pk=None):
        profile = request.user.profile

        try:
            activity = self.get_object()  # Get activity by pk for current user
        except Activity.DoesNotExist:
            return Response(
                {"error": "Activity not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Get updated name from request body
        activity_name = request.data.get("name")
        if not activity_name:
            return Response(
                {"error": "Activity name is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        activity.update_name(activity_name)  # Assuming you have this method

        try:
            profile.add_activity(profile.activity_timer.elapsed_time)
            xp_reward = profile.activity_timer.complete()
            profile.activity_timer.refresh_from_db()
            profile.add_xp(xp_reward)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Return latest activities (today’s or recent 5)
        activities = Activity.objects.filter(
            profile=profile, created_at__date=timezone.now().date()
        ).order_by("-created_at")
        if not activities.exists():
            activities = Activity.objects.filter(profile=profile).order_by(
                "-created_at"
            )[:5]

        activities_list = ActivitySerializer(activities, many=True).data
        profile_data = ProfileSerializer(profile).data

        message_text = f"Activity submitted. You got {xp_reward} XP!"
        ServerMessage.objects.create(
            group=profile.group_name,
            type="notification",
            action="notification",
            data={},
            message=message_text,
            is_draft=False,
        )

        return Response(
            {
                "success": True,
                "message": "Activity submitted",
                "profile": profile_data,
                "activities": activities_list,
                "activity_rewards": xp_reward,
            }
        )


class QuestViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestSerializer

    def get_queryset(self):
        return Quest.objects.all()

    def list(self, request):
        quests = self.get_queryset()
        serializer = QuestSerializer(quests, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def eligible(self, request):
        profile = request.user.profile
        try:
            character = PlayerCharacterLink.get_character(profile)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        eligible_quests = check_quest_eligibility(character, profile)
        serializer = QuestSerializer(
            eligible_quests, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def choose(self, request):
        profile = request.user.profile
        quest_id = request.data.get("quest_id")
        if not quest_id:
            return Response(
                {"error": "quest_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        quest = get_object_or_404(Quest, id=quest_id)

        try:
            character = PlayerCharacterLink.get_character(profile)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        duration = request.data.get("duration")
        try:
            character.quest_timer.change_quest(quest, duration)
            character.quest_timer.refresh_from_db()
        except Exception as e:
            return Response(
                {"error": "Failed to change quest: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        quest_timer_data = QuestTimerSerializer(
            character.quest_timer, context={"request": request}
        ).data
        return Response(
            {
                "success": True,
                "quest_timer": quest_timer_data,
                "message": f"Quest {quest.name} selected",
            }
        )

    @action(detail=False, methods=["post"])
    def complete(self, request):
        profile = request.user.profile
        try:
            character = PlayerCharacterLink.get_character(profile)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile.activity_timer.refresh_from_db()
            character.quest_timer.refresh_from_db()
            completion_data = character.complete_quest()
            if completion_data is None:
                return Response(
                    {"error": "Quest completion failed."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        except Exception as e:
            return Response(
                {"error": "Failed to complete quest: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        eligible_quests = check_quest_eligibility(character, profile)
        quests_data = QuestSerializer(
            eligible_quests, many=True, context={"request": request}
        ).data
        character_data = CharacterSerializer(
            character, context={"request": request}
        ).data

        return Response(
            {
                "success": True,
                "message": "Quest completed",
                "xp_reward": 5,
                "quests": quests_data,
                "character": character_data,
                "activity_timer_status": profile.activity_timer.status,
                "quest_timer_status": character.quest_timer.status,
                "completion_data": completion_data,
            }
        )


class BaseTimerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Abstract base class for timer viewsets. Assumes each timer
    is linked to a profile, and enforces IsAuthenticated + IsOwnerProfile.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Default queryset logic (override if needed)
        return self.queryset.filter(profile=self.request.user.profile)

    def handle_related_object(self, related_model, related_id, related_name="object"):
        """
        Generic helper to fetch a related model instance and return a DRF Response on failure.
        """
        try:
            return related_model.objects.get(id=related_id), None
        except related_model.DoesNotExist:
            return None, Response(
                {"error": f"{related_name.capitalize()} not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def control_timer(self, request, pk, command):
        timer = self.get_object()

        # Map commands to timer methods
        commands_map = {
            "start": timer.start,
            "pause": timer.pause,
            "complete": timer.complete,
            "reset": timer.reset,
        }

        if command not in commands_map:
            return Response({"error": "Invalid command"}, status=400)

        try:
            commands_map[command]()
            serializer = self.get_serializer(timer)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        return self.control_timer(request, pk, "start")

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        return self.control_timer(request, pk, "pause")

    @action(detail=True, methods=["post"])
    def reset(self, request, pk=None):
        return self.control_timer(request, pk, "reset")

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        return self.control_timer(request, pk, "complete")


class ActivityTimerViewSet(BaseTimerViewSet):
    serializer_class = ActivityTimerSerializer
    queryset = ActivityTimer.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerProfile]

    def get_queryset(self):
        return ActivityTimer.objects.filter(profile=self.request.user.profile)

    @action(detail=True, methods=["post"])
    def set_activity(self, request, pk=None):
        timer = self.get_object()
        activity_id = request.data.get("activity_id")

        activity, error_response = self.handle_related_object(
            Activity, activity_id, "activity"
        )
        if error_response:
            return error_response

        timer.new_activity(activity)
        serializer = self.get_serializer(timer)
        return Response(serializer.data)


class QuestTimerViewSet(BaseTimerViewSet):
    serializer_class = QuestTimerSerializer
    queryset = QuestTimer.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerCharacter]

    def get_queryset(self):
        profile = self.request.user.profile
        active_character_ids = PlayerCharacterLink.objects.filter(
            profile=profile, is_active=True
        ).values_list("character_id", flat=True)

        return QuestTimer.objects.filter(character_id__in=active_character_ids)

    @action(detail=True, methods=["post"])
    def change_quest(self, request, pk=None):
        timer = self.get_object()
        quest_id = request.data.get("quest_id")
        duration = request.data.get("duration")

        quest, error_response = self.handle_related_object(Quest, quest_id, "quest")
        if error_response:
            return error_response

        if not isinstance(duration, int):
            return Response(
                {"error": "Duration must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        timer.change_quest(quest, duration)
        serializer = self.get_serializer(timer)
        return Response(serializer.data)


class DownloadUserDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key="ip", rate="10/h", method="GET", block=True))
    @transaction.atomic
    def get(self, request):
        user = request.user
        profile = user.profile
        try:
            character_obj = PlayerCharacterLink().get_character(profile)
        except Character.DoesNotExist:
            logger.error(
                f"Character not found for user {user.username} (ID: {user.id})."
            )
            raise Http404("Character data not found.")

        activities_json = ActivitySerializer(profile.activities.all(), many=True).data
        user_data = {
            "email": user.email,
            "profile": {
                "id": profile.id,
                "profile_name": profile.name,
                "level": profile.level,
                "xp": profile.xp,
                "bio": profile.bio,
                "total_time": profile.total_time,
                "total_activities": profile.total_activities,
                "is_premium": profile.is_premium,
            },
            "activities": activities_json,
            "character": {
                "id": character_obj.id,
                "character_name": character_obj.name,
                "level": character_obj.level,
                "total_quests": character_obj.total_quests,
            },
        }

        logger.info(
            f"User {user.username} (ID: {user.id}) initiated download of their data."
        )
        logger.info(
            f"User {user.username} (ID: {user.id}) successfully downloaded their data."
        )

        return Response(user_data)


class DeleteAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        logger.info(f"User {user.username} (ID: {user.id}) initiated account deletion.")

        user.pending_deletion = True
        user.delete_at = timezone.now() + timezone.timedelta(days=14)
        user.save()

        send_mail(
            "Account Deletion Scheduled",
            "Hello,\nYour account will be deleted in 14 days. If you wish to cancel the deletion, please log in again.\nThank you for using Progress, and we're sorry to see you go!",
            "admin@progressrpg.com",
            [user.email],
            fail_silently=False,
        )

        # Flush session
        request.session.flush()
        logout(request)

        logger.info(
            f"[DELETE ACCOUNT] User {user.id} logged out and scheduled for soft delete."
        )

        return Response(
            {"detail": "Account deletion scheduled. You have been logged out."},
            status=status.HTTP_200_OK,
        )

    def get(self, request):
        # Optional: could return some info or just method not allowed
        return Response(
            {"detail": "Use POST to delete your account."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
