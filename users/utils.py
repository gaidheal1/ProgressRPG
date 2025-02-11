# users.utils
from character.models import Character, PlayerCharacterLink

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