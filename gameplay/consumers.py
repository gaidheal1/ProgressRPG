#from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
#from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.db import transaction
#from django.utils.timezone import now
import json, logging

from .models import ServerMessage
from .utils import process_completion, process_initiation, control_timers

logger = logging.getLogger("django")


class TimerConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        from django.contrib.auth.models import AnonymousUser
        user = self.scope.get("user", AnonymousUser())
        if user and user.is_authenticated:
            logger.info(f"[CONNECT] Authenticated user {user.id}. Connecting...")

            if hasattr(self, 'profile_group') and self.profile_group in self.channel_layer.groups:
                logger.warning(f"[CONNECT] User {user.username} already connected to a WebSocket.")
                await self.close()  # Reject the new connection
                return
            
            self.profile, self.character = await self.set_profile_and_character(user)

            await self.accept()
            logger.info(f"[CONNECT] WebSocket connection accepted for profile {self.profile.id}")
            
            self.profile_group = f"profile_{self.profile.id}"
            await self.channel_layer.group_add(self.profile_group, self.channel_name)
            #logger.debug(f"[CONNECT] Consumer {self.channel_name} joined group: {self.profile_group}")

            #logger.info(f"Consumer subscribed to: {self.profile_group}")
            #logger.info(f"Sending message to: profile_{profile.id}")
            
            await self._send_pending_messages()

            self.activity_timer = await self.get_activity_timer()
            self.quest_timer = await self.get_quest_timer()

            await self.send_json({
                "type": "console.log", 
                "action": "console.log", 
                "message": "Server: Successful websocket connection",
            })
        else:
            logger.warning(f"[CONNECT] Unauthenticated user attempted connection.")
            await self.close()


    async def disconnect(self, close_code):
        logger.info(f"[DISCONNECT] WebSocket disconnecting with close code: {close_code}")

        if hasattr(self, "profile_group"):
            logger.info(f"[DISCONNECT] Removed from group: {self.profile_group}")
            await self.channel_layer.group_discard(self.profile_group, self.channel_name)

        if hasattr(self, "profile") and hasattr(self, "character"):
            logger.info(f"Pausing timers for profile {self.profile.id}; websocket disconnected")
            if self.activity_timer.status not in ["completed", "empty", "paused"] or self.quest_timer.status not in ["completed", "empty", "paused"]:
                await control_timers(self.profile, self.activity_timer, self.quest_timer, "pause")

        # if close_code != 1000:
        #     logger.warning(f"Unexpected disconnect: {close_code}")
        #raise StopConsumer()


    async def test_message(self, event):
        logger.info(f"[TEST MESSAGE] Received test message: {event}")
        await self.send_json({
            "type": "console.log",
            "action": "console.log",
            "message": f"Test message received: {event.get('message')}"
        })

    async def group_message(self, event):
        """
        Handle messages sent to the WebSocket group.
        """
        logger.info(f"[GROUP MESSAGE] Relaying group message. Event: {event}")
        

    async def receive_json(self, event, **kwargs):
        message_type = event.get("type")
        if message_type == "ping":
            logger.debug(f"[RECEIVE JSON] Message received: {event}, type: {message_type}")
        else:
            logger.info(f"[RECEIVE JSON] Message received: {event}, type: {message_type}")

        await database_sync_to_async(self.quest_timer.refresh_from_db)()
        if message_type:
            logger.debug(f"[RECEIVE JSON] Processing type: {message_type}")
            if message_type == "client_request":
                #logger.debug(f"[RECEIVE JSON] Sending to handle_client_request")
                await self.handle_client_request(event)
            elif message_type == "ping":
                await self.send_json({"type": "pong", "action": "pong", "message": "pong"})
                if self.quest_timer.status != "completed":
                    logger.debug(f"[RECEIVE JSON] Quest status: {self.quest_timer.status}")
                    time_finished = await database_sync_to_async(self.quest_timer.time_finished)()
                    if time_finished:
                        logger.debug(f"[RECEIVE JSON] Quest timer is finished? {time_finished}")
                        await database_sync_to_async(process_completion)(self.profile, self.character, "complete_quest")

            else: logger.warning(f"[RECEIVE JSON] Unknown type received: {message_type}")
        else:
            logger.warning(f"[RECEIVE JSON] Received data without type: {event}")

    async def action(self, event):
        logger.info(f"[HANDLE ACTION] Handling action: {event}")
        message_type = event.get("type")
        #logger.debug(f"[HANDLE ACTION] Received type {message_type} with action {event.get("action")}")
        
        if self.channel_name:  # If WebSocket is open
            #logger.debug(f"[HANDLE ACTION] Sending action: {event}")
            await self.send_json(event)
        else:
            # Store the action for later if WebSocket is closed
            await self.store(event)
    
    @database_sync_to_async
    def store(self, event):
        """Store the action in the ServerMessage model if the WebSocket is closed"""
        logger.info(f"[STORE ACTION] Storing action: {event}")
        ServerMessage.objects.create(
            profile=self.profile, 
            type=event.get("type"),
            action=event["action"],
            data=event.get("data", {}),
            message=event.get("message", ""),
            is_delivered=False
        )


    async def handle_client_request(self, message):
        logger.info(f"[HANDLE CLIENT REQUEST] Handling client request: {message}")
        action = message.get("action")

        if action == "start_timers":
            await control_timers(self.profile, self.activity_timer, self.quest_timer, "start")
        elif action == "pause_timers":
            await control_timers(self.profile, self.activity_timer, self.quest_timer, "pause")
        elif action in ["create_activity", "choose_quest"]:
            #qt = self.quest_timer
            #logger.debug(f"[HANDLE CLIENT REQUEST] Quest timer status/dur/elapsed/remaining: {qt.status}/{qt.duration}/{qt.get_elapsed_time()}/{qt.get_remaining_time()}")
            success = await database_sync_to_async(process_initiation)(self.profile, self.character, action)
            if not success:
                logger.warning(f"[HANDLE CLIENT REQUEST] Failed to initiate {action}.")
        elif action in ["complete_quest", "submit_activity"]:
            if action == "complete_quest" and self.quest_timer.status not in ["active", "waiting", "paused"]:
                logger.warning(f"[HANDLE CLIENT REQUEST] Cannot complete quest: Invalid status {self.quest_timer.status}")
                return
            
            success = await database_sync_to_async(process_completion)(self.profile, self.character, action)
            logger.debug(f"[HANDLE CLIENT REQUEST] {action} result: {success}")
            if not success:
                logger.warning(f"[HANDLE CLIENT REQUEST] Failed to complete {action}, result: {success}")
            
        else:
            logger.warning(f"[HANDLE CLIENT REQUEST] Unknown action: {action}")


        
    @database_sync_to_async
    def set_profile_and_character(self, user):
        with transaction.atomic():
            logger.debug(f"[SET PROFILE] Setting profile and character for user: {user.username}")
            from character.models import PlayerCharacterLink
            character = PlayerCharacterLink().get_character(user.profile)
            return user.profile, character
    
    @database_sync_to_async
    def get_activity_timer(self):
        logger.debug(f"[GET ACTIVITY TIMER] Fetching activity timer for profile: {self.profile.id}")
        from .models import ActivityTimer
        return ActivityTimer.objects.filter(profile=self.profile).first()
    
    @database_sync_to_async
    def get_quest_timer(self):
        logger.debug(f"[GET QUEST TIMER] Fetching quest timer for character: {self.character.id}")
        from .models import QuestTimer
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


    async def server_message(self, event):
        logger.info(f"[SERVER MESSAGE] Preparing to send message: {event}")

        message_type = event.get("type")
        if message_type == "server_message":
            data = event.get("data")
        else:
            data = event
        
        if isinstance(data, dict):
            await self.send_json(data)
            logger.info(f"[SERVER MESSAGE] Sent message: {data}")

        else:
            # Handle if data is not a dict
            logger.error(f"[SERVER MESSAGE] Unexpected data type: {type(data)} - {data}")
            await self.send_json({"error": "Invalid data type", "message": f"Received data of type {type(data)}"})


    async def error(self, event):
        #data = event.get("data", {})
        logger.error(f"[ERROR] Sending error message from event: {event}")
        await self.send_json(event)
        
    async def send_pending_messages(self, event):
        """
        Send pending messages to the client.
        """
        logger.info(f"[SEND PENDING MESSAGES (event handler)] Sending pending messages to profile {self.profile.id}.")
        await self._send_pending_messages()


    async def _send_pending_messages(self):
        """
        Fetch and send all pending messages for the connected profile.
        Marks successfully sent messages as delivered.
        """
        logger.info(f"[SEND PENDING MESSAGES] Fetching pending messages for profile {self.profile.id}.")
        from .models import ServerMessage

        get_unread_messages = database_sync_to_async(lambda profile: list(ServerMessage.get_unread(profile)))
        messages = await get_unread_messages(self.profile)

        if not messages:
            logger.info(f"[SEND PENDING MESSAGES] No pending messages for profile {self.profile.id}.")
            return
        logger.info(f"[SEND PENDING MESSAGES] Found {len(messages)} pending messages for profile {self.profile.id}.")

        successful_message_ids = []
        for message in messages:
            try:
                message_dict = message.to_dict()
                await self.send_json(message_dict)
                successful_message_ids.append(message.id)
                logger.info(f"[SEND PENDING MESSAGES] Successfully sent message {message.id}.")
            except Exception as e:
                logger.error(f"[SEND PENDING MESSAGES] Failed to send message {message.id}: {e}")

        # Mark successfully sent messages as delivered
        if successful_message_ids:
            await database_sync_to_async(
                lambda: ServerMessage.objects.filter(id__in=successful_message_ids).update(is_delivered=True)
            )()
            logger.info(f"[SEND MESSAGES] Marked {len(successful_message_ids)} messages as delivered.")
        else:
            logger.info(f"[SEND MESSAGES] No messages were marked as delivered.")
