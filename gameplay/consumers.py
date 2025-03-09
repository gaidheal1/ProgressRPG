import json
import django
from django.apps import apps
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from django.db import transaction

django.setup()

from .models import ActivityTimer, QuestTimer
from character.models import PlayerCharacterLink
from .utils import start_timers, pause_timers
import logging

logger = logging.getLogger("django")

class TimerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user", AnonymousUser())
        if user and user.is_authenticated:
            logger.info(f"[CONNECT] Authenticated user connecting: {user.username}")
            self.profile, self.character = await self.set_profile_and_character(user)
            self.profile_group = f"profile_{self.profile.id}"
            await self.channel_layer.group_add(self.profile_group, self.channel_name)
            await self.accept()
            logger.debug(f"[CONNECT] WebSocket connection accepted for profile {self.profile.id}")
            self.activity_timer = await self.get_activity_timer()
            self.quest_timer = await self.get_quest_timer()

            logger.debug(f"Starting timers for profile {self.profile.id}")
            if hasattr(self, "profile") and hasattr(self, "character"):
                start_timers(self.profile.id, self.activity_timer, self.quest_timer)

            await self.send(text_data=json.dumps({
                "action": "console.log", 
                "message": "Server: Successful websocket connection",
            }))
        else:
            logger.warning(f"[CONNECT] Unauthenticated user attempted connection.")
            await self.close()

    async def disconnect(self, close_code):
        logger.info(f"[DISCONNECT] WebSocket disconnecting with close code: {close_code}")
        if hasattr(self, "profile_group"):
            logger.debug(f"[DISCONNECT] Removed from group: {self.profile_group}")
            await self.channel_layer.group_discard(self.profile_group, self.channel_name)

        if hasattr(self, "profile") and hasattr(self, "character"):
            logger.debug(f"Pausing timers for profile {self.profile.id}; websocket disconnected")
            pause_timers(self.profile.id, self.activity_timer, self.quest_timer)

    async def receive(self, text_data):
        try:
            logger.info(f"[RECEIVE] Message received: {text_data}")
            data = json.loads(text_data)
            action = data.get("action")

            if action:
                logger.debug(f"[RECEIVE] Processing action: {action}")
                if action == "ping":
                    await self.send(text_data=json.dumps({"action": "pong", "message": "pong"}))
                elif action == "start_timers_request":
                    await start_timers(self.profile.id, self.activity_timer, self.quest_timer)
                elif action == "pause_timers_request":
                    await pause_timers(self.profile.id, self.activity_timer, self.quest_timer)
                else:logger.warning(f"[RECEIVE] Unknown action received: {action}")
            else:
                logger.warning(f"[RECEIVE] Received data without action: {data}")
        except json.JSONDecodeError as e:
            logger.error(f"[RECEIVE] Error decoding JSON: {e}")

    async def group_message(self, event):
        """
        Handle messages sent to the WebSocket group.
        """
        data = event['data']
        logger.info(f"[GROUP MESSAGE] Relaying group message: {data}")
        await self.send(text_data=json.dumps(data))

        
    @database_sync_to_async
    def set_profile_and_character(self, user):
        with transaction.atomic():
            logger.debug(f"[SET PROFILE] Setting profile and character for user: {user.username}")
            character = PlayerCharacterLink().get_character(user.profile)
            return user.profile, character
    
    @database_sync_to_async
    def get_activity_timer(self):
        logger.debug(f"[GET ACTIVITY TIMER] Fetching activity timer for profile: {self.profile.id}")
        return ActivityTimer.objects.filter(profile=self.profile).first()
    
    @database_sync_to_async
    def get_quest_timer(self):
        logger.debug(f"[GET QUEST TIMER] Fetching quest timer for character: {self.character.id}")
        return QuestTimer.objects.filter(character=self.character).first()

    async def send_timer_update(self, event):
        logger.debug(f"[SEND TIMER UPDATE] Sending timer update: {event['data']}")
        await self.send(text_data=json.dumps(event["data"]))
    
    def get_activity_time(self):
        """Get the current activity time."""
        logger.debug(f"[GET ACTIVITY TIME] Fetching elapsed activity time.")
        return self.activity_timer.get_elapsed_time() if self.activity_timer else None
    
    def get_quest_time(self):
        """Get the current quest time."""
        logger.debug(f"[GET QUEST TIME] Fetching elapsed quest time.")
        return self.quest_timer.get_elapsed_time() if self.quest_timer else None
    
    async def timer_update(self):
        """Receive timer updates from the group."""
        logger.debug(f"[TIMER UPDATE] Sending timer updates to the client.")
        await self.send(json.dumps({
            "activity_time": self.get_activity_time(),
            "quest_time": self.get_quest_time(),
        }))

