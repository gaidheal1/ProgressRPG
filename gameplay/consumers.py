import json
import asyncio
import django
from django.apps import apps
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.db import transaction

django.setup()

from .models import ActivityTimer, QuestTimer, Activity, Quest, PlayerCharacterLink, QuestResults
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
        
    @database_sync_to_async
    def set_profile_and_character(self, user):
        with transaction.atomic():
            character = PlayerCharacterLink().get_character(user.profile)
            data = {
                "profile" : user.profile,
                "character" : character if character else None
            }
            return data
    
    @database_sync_to_async
    def get_activity_timer(self):
        return ActivityTimer.objects.filter(profile=self.profile).first()
    
    @database_sync_to_async
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
        for quest in eligible_quests:
            quest.save()
        print(eligible_quests[0])
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
        current_activity = ActivitySerializer(self.activity_timer.activity).data if self.activity_timer.status != 'empty' else False
        current_quest = QuestSerializer(self.quest_timer.quest).data if self.quest_timer.status != 'empty' else False
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
    def _choose_quest_db(self, quest_id):
        with transaction.atomic():
            quest = Quest.objects.get(id=quest_id)
            self.quest_timer.change_quest(quest) # add duration as second argument later
            quest_serializer = QuestSerializer(quest)
            return quest_serializer.data
        
    async def choose_quest(self, quest_id):
        data = await self._choose_quest_db(quest_id)
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
        self.activity_timer.pause()
        self.quest_timer.pause()

    @database_sync_to_async
    def _create_activity_db(self, activity_name):
        with transaction.atomic():
            print("Inside create_activity function")
            activity = Activity.objects.create(profile=self.profile, name=activity_name)
            self.activity_timer.new_activity(activity)
            return activity

    async def create_activity(self, activity_name):
        activity = await self._create_activity_db(activity_name)
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
        if self.activity_timer.status != 'empty':
            self.activity_timer.update_name(new_name)

    async def update_activity_name(self, new_name):
        print(f"Updating activity name to: {new_name}")
        await self._update_activity_name(new_name)
        await self.send(text_data=json.dumps({
            "type": "update_activity_name_response",
            "success": True,
            "message": "Activity name updated",
            "new_name": new_name
        }))

    @database_sync_to_async
    def _submit_activity_db(self):
        with transaction.atomic():
            self.profile.add_activity(self.activity_timer.elapsed_time)
            xp_reward = self.activity_timer.complete()
            self.profile.add_xp(xp_reward)
            profile_serializer = ProfileSerializer(self.profile)
            activities = Activity.objects.filter(profile=self.profile, created_at__date=now().date())
            activities_list = ActivitySerializer(activities, many=True)
            data = {
                "profile": profile_serializer.data,
                "activities": activities_list.data,
            }
            return data

    async def submit_activity(self):
        await self.stop_timers()
        data = await self._submit_activity_db()
        await self.send(text_data=json.dumps({
            "type": "submit_activity_response",
            "success": True,
            "message": "Activity submitted",
            "profile": data["profile"],
            "activities": data["activities"],
        }))

    @database_sync_to_async
    def _quest_completed_db(self):
        with transaction.atomic():
            self.character.complete_quest(self.quest_timer.quest)
            xp_reward = self.quest_timer.complete()
            self.character.add_xp(xp_reward)
            eligible_quests = check_quest_eligibility(self.character, self.profile)
            character = CharacterSerializer(self.character)
            quests = QuestSerializer(eligible_quests, many=True)
            return character.data, quests.data

    async def quest_completed(self):
        await self.stop_timers()
        character, quests = await self._quest_completed_db()
        await self.send(text_data=json.dumps({
            "type": "quest_completed_response",
            "success": True,
            "message": "Quest completed",
            "xp_reward": 5,
            "character": character,
            "quests": quests,
        }))

