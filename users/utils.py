# users.utils

from character.models import Character, PlayerCharacterLink
from gameplay.models import QuestTimer, Quest
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.timezone import now, timedelta
import logging

logger = logging.getLogger("django")

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

         qt, created = QuestTimer.objects.get_or_create(character=character)
         tut_quest = Quest.objects.filter(name="[TUTORIAL] Getting started").first()
         if not tut_quest:
              logger.warning(f"Tutorial quest '[TUTORIAL] Getting started' not found!")
              raise ValueError("Tutorial quest '[TUTORIAL] Getting started' not found!")

         if created or profile.created_at > (now() - timedelta(days=14)):
              qt.change_quest(tut_quest, 60)

def send_signup_email(user):
     """Emails to send when a new user is created"""
     admin_email = 'admin@progressrpg.com'
     subject = 'Welcome to Progress!'
     message = render_to_string(
          'emails/welcome_email.html',
          {'user': user, 'current_year': 2025}
     )

     from_email = settings.DEFAULT_FROM_EMAIL
     recipients_list = [user.email, admin_email]

     send_mail(
          subject,
          message,
          from_email,
          recipients_list,
          fail_silently=False,  # Set to False to raise errors if email fails
          html_message=message
     )