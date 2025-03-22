"""
Utility Functions for User Management

This module provides utility functions to support user-related operations, such as
assigning characters to profiles and sending user notifications. These utilities
are designed to streamline key processes in the application, enhancing user experience
and ensuring consistency in functionality.

Functions:
    - assign_character_to_profile(profile): Assigns a default NPC character to a profile,
      deactivates any previously linked character, and optionally assigns a tutorial quest.
    - send_signup_email(user): Sends a welcome email to new users, introducing them to the platform.

Usage:
These functions are essential for managing user interactions and onboarding, ensuring that
new users are properly initialized with characters and receive email notifications during
the account creation process.

Author:
    Duncan Appleby

"""
from character.models import Character, PlayerCharacterLink
from gameplay.models import QuestTimer, Quest
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.timezone import now, timedelta
import logging

logger = logging.getLogger("django")

def assign_character_to_profile(profile):
    """
    Assign a default Character (non-player character) to the given Profile. Deactivates
    any currently active character and associates a new NPC with the Profile. If the
    Profile is recent, assigns a tutorial quest to the newly linked character.

    :param profile: The Profile to which a character will be assigned.
    :type profile: Profile
    :raises ValueError: If the tutorial quest is not found in the database.
    """

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
    """
    Send a welcome email to the user after account creation. The email includes a
    greeting and an introduction to the platform.

    :param user: The user who signed up, containing an email and other details.
    :type user: CustomUser
    :raises smtplib.SMTPException: If sending the email fails due to SMTP issues.
    """
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