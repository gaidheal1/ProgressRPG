from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

class MyAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        print("cookies mmm:", scope.get("cookies", {}))

        if scope['type'] == 'http':
            print("http request")
            sessionid = scope.get("cookies", {}).get("sessionid", None)
            if sessionid:
                session = await self.get_session(sessionid)
                if session:
                    user = await self.get_user_from_session(sessionid)
                    if user:
                        scope["user"] = user
                        print(f"User {user} authenticated")
                    else:
                        print("User not found")
                else:
                    scope["user"] = AnonymousUser()
        elif scope['type'] == 'websocket':
            print("websocket request")
            user = scope.get("user", AnonymousUser())
            if user and user.is_authenticated:
                print("User found!")
            else:
                print("User not found")
        else:
            print("No sessionid found")
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_session(self, sessionid):
        try:
            return Session.objects.get(session_key=sessionid)
        except Session.DoesNotExist:
            return None
        
    @database_sync_to_async
    def get_user_from_session(self, sessionid):
        
        #User = get_user_model()
        try:
            session = Session.objects.get(pk=sessionid)
            user_id = session.get_decoded().get("_auth_user_id")
            return get_user_model().objects.get(id=user_id)
        except (Session.DoesNotExist, get_user_model().DoesNotExist):
            return AnonymousUser()