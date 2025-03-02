# users.utils

from character.models import Character, PlayerCharacterLink
from gameplay.models import QuestTimer
from django.core.mail import send_mail
from django.conf import settings

def assign_character_to_profile(profile):
    """Utility function to assign a Character to a Profile"""

    PlayerCharacterLink.objects.filter(profile=profile, is_active=True).update(is_active=False)
    
    character = Character.objects.filter(is_npc=True, death_date__isnull=True).first()    

    if character:
         PlayerCharacterLink.objects.create(
              profile=profile,
              character=character,
              is_active=True,
         )
         character.is_npc = False
         character.save()

         qt = QuestTimer.objects.get_or_create(character=character)

def send_signup_email(user):
     """Email admin when a new user is created"""
     admin_email = 'admin@progressrpg.com'
     subject = 'New User Signed Up'
     message = f'A new user has signed up.\nUsername: {user.profile.name}\nEmail address: {user.email}'

     send_mail(
          subject,
          message,
          settings.DEFAULT_FROM_EMAIL,  # The "from" email
          [admin_email],  # The recipient list (just the admin for now)
          fail_silently=False,  # Set to False to raise errors if email fails
     )