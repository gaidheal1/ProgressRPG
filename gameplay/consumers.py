import json
import asyncio
import django
from django.apps import apps
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

django.setup()

from .models import ActivityTimer, QuestTimer, Activity, Quest, Character, QuestResults
from .serializers import QuestSerializer, ActivitySerializer, CharacterSerializer
from users.models import Profile
from users.serializers import ProfileSerializer
from .utils import check_quest_eligibility

class ProfileConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user", AnonymousUser())
        if user and user.is_authenticated:
            data = await self.set_profile_and_character(user)
            self.profile = data["profile"]
            self.character = data["character"]
            self.profile_group = f"profile_{self.profile.id}"
            await self.channel_layer.group_add(self.profile_group, self.channel_name)
            await self.accept()

            self.activity_timer = await self.get_activity_timer()
            self.quest_timer = await self.get_quest_timer()

            await self.fetch_activities()
            await self.fetch_quests()
            await self.fetch_info()
        else:
            print("c'est pas un user lol")
            await self.close()
        await self.send(text_data=json.dumps({
            "type": "console.log", 
            "message": "Success",

        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.profile_group, self.channel_name)

    async def receive(self, text_data):
        try:
            message = json.loads(text_data)
            print("Received data:", message)
            action = message.get("action")
            if action == "ping":
                await self.send(text_data=json.dumps({"type": "pong"}))
            elif action == "fetch_activities":
                await self.fetch_activities()
            elif action == "fetch_quests":
                await self.fetch_quests()
            elif action == "fetch_info":
                await self.fetch_info()
            elif action == "choose_quest":
                await self.choose_quest(message["quest_id"])
            elif action == "start_timers":
                await self.start_timers()
            elif action == "stop_timers":
                await self.stop_timers()
            elif action == "create_activity":
                await self.create_activity(message["activity_name"])
            elif action == "update_activity_name":
                await self.update_activity_name(message["activity_name"])
            elif action == "submit_activity":
                await self.submit_activity()
            elif action == "quest_completed":
                await self.quest_completed()
        except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
        
    @sync_to_async
    def set_profile_and_character(self, user):
        data = {
            "profile" : user.profile,
            "character" : Character.objects.get(profile=user.profile)
        }
        return data
    
    @sync_to_async
    def get_activity_timer(self):
        return ActivityTimer.objects.filter(profile=self.profile).first()
    
    @sync_to_async
    def get_quest_timer(self):
        return QuestTimer.objects.filter(character=self.character).first()
    
    async def timer_update(self):
        """Receive timer updates from the group."""
        await self.send(json.dumps({
            "activity_time": self.get_activity_time(),
            "quest_time": self.get_quest_time(),
        }))

    def get_activity_time(self):
        """Get the current activity time."""
        return self.activity_timer.get_elapsed_time() if self.activity_timer else None
    
    def get_quest_time(self):
        """Get the current quest time."""
        return self.quest_timer.get_elapsed_time() if self.quest_timer else None
    
    @database_sync_to_async
    def fetch_activities_db(self):
        #print("Server: Fetching activities")
        activities = Activity.objects.filter(profile=self.profile, created_at__date=now().date())
        serializer = ActivitySerializer(activities, many=True)
        #print("activities:", serializer.data)
        return serializer.data

    async def fetch_activities(self):
        activities_data = await self.fetch_activities_db()
        await self.send(text_data=json.dumps({
            "type": "fetch_activities_response",
            "success": True,
            "activities": activities_data,
            "message": "Activities fetched"
        }))

    @database_sync_to_async
    def fetch_quests_db(self):
        print("Inside fetch_quests_db")
        eligible_quests = check_quest_eligibility(self.character, self.profile)
        serializer = QuestSerializer(eligible_quests, many=True)
        #print("quests:", serializer.data)
        return serializer.data
    
    async def fetch_quests(self):
        quests_data = await self.fetch_quests_db()
        await self.send(text_data=json.dumps({
            "type": "fetch_quests_response",
            "success": True,
            "quests": quests_data,
            "message": "Eligible quests fetched"
        }))

    @database_sync_to_async
    def fetch_info_db(self):
        print("Server: Fetching profile and character info")
        profile_serializer = ProfileSerializer(self.profile)
        character_serializer = CharacterSerializer(self.character)
        current_activity = ActivitySerializer(self.profile.current_activity).data if self.profile.current_activity else False
        current_quest = QuestSerializer(self.character.current_quest).data if self.character.current_quest else False
        data = {
            "profile": profile_serializer.data,
            "character": character_serializer.data,
            "current_activity": current_activity,
            "current_quest": current_quest,
        }
        return data
        
    async def fetch_info(self):
        data = await self.fetch_info_db()
        await self.send(text_data=json.dumps({
            "type": "fetch_info_response",
            "success": True,
            "profile": data["profile"],
            "character": data["character"],
            "current_activity": data["current_activity"],
            "current_quest": data["current_quest"],
            "message": "Profile and character fetched"
        }))

    @database_sync_to_async
    def choose_quest_db(self, quest_id):
        quest = Quest.objects.get(id=quest_id)
        self.character.current_quest = quest
        self.character.save()
        quest_timer, created = QuestTimer.objects.get_or_create(character=self.character)
        if created:
            quest_timer.duration = quest.duration
        quest_serializer = QuestSerializer(quest)
        return quest_serializer.data
        
    async def choose_quest(self, quest_id):
        data = await self.choose_quest_db(quest_id)
        await self.send(text_data=json.dumps({
            "type": "choose_quest_response",
            "success": True,
            "quest": data,
            "message": f"Quest selected"
        }))

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

    @database_sync_to_async
    def create_activity_db(self, activity_name):
        print("Inside create_activity function")
        activity = self.profile.current_activity or Activity.objects.create(profile=self.profile, name=activity_name)
        self.profile.current_activity = activity
        
        activity.save()
        self.profile.save()
        return activity

    async def create_activity(self, activity_name):
        activity = await self.create_activity_db(activity_name)
        await self.send(text_data=json.dumps({
            "type": "create_activity_response",
            "success": True,
            "message": "Activity ready",
            "activity": {
                "id": activity.id,
                "name": activity.name,
            },
        }))

    @database_sync_to_async
    def update_activity_name_db(self, new_name):
        if self.profile.current_activity:
            self.profile.current_activity.name = new_name
            self.profile.current_activity.save()

    async def update_activity_name(self, new_name):
        print(f"Updating activity name to: {new_name}")
        await self.send(text_data=json.dumps({
            "type": "update_activity_name_response",
            "success": True,
            "message": "Activity name updated",
            "new_name": new_name
        }))

    @database_sync_to_async
    def submit_activity_db(self):
        activity = self.profile.current_activity
        activity.add_time(self.activity_timer.elapsed_time)
        self.profile.current_activity.add_time(self.activity_timer.elapsed_time)
        self.activity_timer.reset()
        profile_serializer = ProfileSerializer(self.profile)
        rewards = self.profile.submit_activity()
        activities = Activity.objects.filter(profile=self.profile, created_at__date=now().date())
        activities_list = ActivitySerializer(activities, many=True)
        data = {
            "profile": profile_serializer.data,
            "rewards": rewards,
            "activities": activities_list.data,
        }
        return data

    async def submit_activity(self):
        print("Profile current activity before:", self.profile.current_activity)
        await self.stop_timers()
        data = await self.submit_activity_db()
        print("Profile current activity after:", self.profile.current_activity)
        await self.send(text_data=json.dumps({
            "type": "submit_activity_response",
            "success": True,
            "message": "Activity submitted",
            "profile": data["profile"],
            "activities": data["activities"],
            "activity_rewards": data["rewards"],
        }))

    @sync_to_async
    def quest_completed_db(self):
        self.quest_timer.reset()
        self.character.complete_quest()
        eligible_quests = check_quest_eligibility(self.character, self.profile)
        character = CharacterSerializer(self.character)
        quests = QuestSerializer(eligible_quests, many=True)
        return character.data, quests.data

    async def quest_completed(self):
        await self.stop_timers()
        character, quests = await self.quest_completed_db()
        await self.send(text_data=json.dumps({
            "type": "quest_completed_response",
            "success": True,
            "message": "Quest completed",
            "xp_reward": 5,
            "character": character,
            "quests": quests,
        }))

