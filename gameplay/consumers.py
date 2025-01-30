import json
import asyncio
import django
from django.apps import apps
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async

django.setup()

from .models import ActivityTimer, QuestTimer

class ProfileConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Called when a WebSocket connection is established."""
        user = self.scope.get("user", AnonymousUser())
        if user and user.is_authenticated:
            self.profile = await self.get_profile(user)    
            self.profile_group = f"user_{self.profile.id}"
            await self.channel_layer.group_add(self.profile_group, self.channel_name)
            await self.accept()
            print("User found!")
        else:
            await self.close()
        
        self.activity_timer = await self.get_activity_timer()
        self.quest_timer = await self.get_quest_timer()

        self.send(text_data=json.dumps({
            "type": "initial_timers",
            "activity_time": self.get_activity_time(),
            "quest_time": self.get_quest_time(),
        }))

    @sync_to_async
    def get_profile(self, user):
        return user.profile
    
    @sync_to_async
    def get_activity_timer(self):
        #ActivityTimer = apps.get_model("gameplay", "ActivityTimer")
        return ActivityTimer.objects.filter(profile=self.profile).first()
    
    @sync_to_async
    def get_quest_timer(self):
        Character = apps.get_model("gameplay", "Character")
        QuestTimer = apps.get_model("gameplay", "QuestTimer")
        character = Character.objects.filter(profile=self.profile).first()
        return QuestTimer.objects.filter(character=character).first()
    
    async def disconnect(self, close_code):
        """Called when a WebSocket connection is closed."""

        await self.channel_layer.group_discard(self.profile_group, self.channel_name)
        print("Timer stopped")

    async def send_timer_updates(self):
        """Send the current timer state to the client."""
        while True:
            activity_time = self.get_activity_time()
            quest_time = self.get_quest_time()
            
            await self.channel_layer.group_send(
                self.profile_group,
                {
                    "type": "timer_update",
                    "activity_time": activity_time,
                    "quest_time": quest_time,
                }
            )
            #await asyncio.sleep(1)

    async def timer_update(self, event):
        """Receive timer updates from the group."""
        await self.send(json.dumps({
            "activity_time": event["activity_time"],
            "quest_time": event["quest_time"],
        }))

    def get_activity_time(self):
        """Get the current activity time."""
        #print("self.activity_timer:", self.activity_timer)
        return self.activity_timer.get_elapsed_time() if self.activity_timer else None
    
    def get_quest_time(self):
        """Get the current quest time."""
        return self.quest_timer.get_elapsed_time() if self.quest_timer else None

    async def receive(self, text_data):
        message = json.loads(text_data)
        action = message.get("action")
        
        if action == "start_timers":
            await self.start_timers()
        elif action == "stop_timers":
            await self.stop_timers()
        elif action == "fetch_activities":
            await self.fetch_activities()
        elif action == "fetch_quests":
            await self.fetch_quests()
        elif action == "fetch_info":
            await self.fetch_info()
        elif action == "choose_quest":
            await self.choose_quest(message["quest_id"])
        elif action == "create_activity_timer":
            await self.create_activity_timer(message["activity_name"])
        elif action == "submit_activity":
            await self.submit_activity()
        elif action == "quest_completed":
            await self.quest_completed()

    @sync_to_async
    def start_timers(self):
        """Start the timer."""
        self.activity_timer.start()
        self.quest_timer.start()
        
    @sync_to_async
    def stop_timers(self):
        """Stop the timer."""
        self.activity_timer.stop()
        self.quest_timer.stop()

    @sync_to_async
    def fetch_activities(self):
        Activity = apps.get_model("gameplay", "Activity")
        activities = Activity.objects.filter(profile=self.profile, created_at__date=now().date())
        serializer = apps.get_model("gameplay", "ActivitySerializer")(activities, many=True)
        self.send(text_data=json.dumps({
            "type": "fetch_activities_response",
            "success": True,
            "activities": serializer.data,
            "message": "Activities fetched"
        }))

    @sync_to_async
    def fetch_quests(self):
        Character = apps.get_model("gameplay", "Character")
        character = Character.objects.get(profile=self.profile)
        eligible_quests = apps.get_model("gameplay", "check_quest_eligibility")(character, self.profile)
        serializer = apps.get_model("gameplay", "QuestSerializer")(eligible_quests, many=True)
        self.send(text_data=json.dumps({
            "type": "fetch_quests_response",
            "success": True,
            "quests": serializer.data,
            "message": "Eligible quests fetched"
        }))

    @sync_to_async
    def fetch_info(self):
        Character = apps.get_model("gameplay", "Character")
        character = Character.objects.get(profile=self.profile)
        profile_serializer = apps.get_model("users", "ProfileSerializer")(self.profile)
        character_serializer = apps.get_model("gameplay", "CharacterSerializer")(character)
        current_activity = {"duration": self.profile.current_activity.duration, "name": self.profile.current_activity.name} if self.profile.current_activity else False
        current_quest = apps.get_model("gameplay", "QuestSerializer")(character.current_quest).data if character.current_quest else False
        self.send(text_data=json.dumps({
            "type": "fetch_info_response",
            "success": True,
            "profile": profile_serializer.data,
            "character": character_serializer.data,
            "current_activity": current_activity,
            "current_quest": current_quest,
            "message": "Profile and character fetched"
        }))

    @sync_to_async
    def choose_quest(self, quest_id):
        Quest = apps.get_model("gameplay", "Quest")
        Character = apps.get_model("gameplay", "Character")
        quest = Quest.objects.get(id=quest_id)
        character = Character.objects.get(profile=self.profile)
        character.current_quest = quest
        character.save()
        quest_timer, created = apps.get_model("gameplay", "QuestTimer").objects.get_or_create(character=character)
        if created:
            quest_timer.duration = quest.duration
        quest_serializer = apps.get_model("gameplay", "QuestSerializer")(quest)
        self.send(text_data=json.dumps({
            "type": "choose_quest_response",
            "success": True,
            "quest": quest_serializer.data,
            "message": f"Quest {quest.name} selected"
        }))

    @sync_to_async
    def create_activity_timer(self, activity_name):
        Activity = apps.get_model("gameplay", "Activity")
        activity = self.profile.current_activity or Activity.objects.create(profile=self.profile, name=activity_name)
        self.profile.current_activity = activity
        timer, created = apps.get_model("gameplay", "ActivityTimer").objects.get_or_create(profile=self.profile)
        activity.save()
        timer.save()
        self.profile.save()
        self.send(text_data=json.dumps({
            "type": "create_activity_timer_response",
            "success": True,
            "message": "Activity timer created and ready"
        }))

    @sync_to_async
    def submit_activity(self):
        Character = apps.get_model("gameplay", "Character")
        character = Character.objects.get(profile=self.profile)
        activity = self.profile.current_activity
        activity_timer = apps.get_model("gameplay", "ActivityTimer").objects.get(profile=self.profile)
        activity_timer.stop()
        activity.add_time(activity_timer.elapsed_time)
        activity_timer.reset()
        apps.get_model("gameplay", "QuestTimer").objects.get(character=character).stop()
        rewards = self.profile.submit_activity()
        activities = apps.get_model("gameplay", "Activity").objects.filter(profile=self.profile, created_at__date=now().date())
        activities_list = [{"name": act.name, "duration": act.duration, "created_at": act.created_at.isoformat()} for act in activities]
        profile_serializer = apps.get_model("users", "ProfileSerializer")(self.profile)
        self.send(text_data=json.dumps({
            "type": "submit_activity_response",
            "success": True,
            "message": "Activity submitted",
            "profile": profile_serializer.data,
            "activities": activities_list,
            "activity_rewards": rewards
        }))

    @sync_to_async
    def quest_completed(self):
        Character = apps.get_model("gameplay", "Character")
        character = Character.objects.get(profile=self.profile)
        quest_timer = apps.get_model("gameplay", "QuestTimer").objects.get(character=character)
        quest_timer.stop()
        quest_timer.reset()
        apps.get_model("gameplay", "ActivityTimer").objects.get(profile=self.profile).stop()
        character.complete_quest()
        eligible_quests = apps.get_model("gameplay", "check_quest_eligibility")(character, self.profile)
        serializer = apps.get_model("gameplay", "QuestSerializer")(eligible_quests, many=True)
        self.send(text_data=json.dumps({
            "type": "quest_completed_response",
            "success": True,
            "message": "Quest completed",
            "xp_reward": 5,
            "eligible_quests": serializer.data
        }))