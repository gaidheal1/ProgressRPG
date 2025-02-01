from .models import Character, PlayerCharacterLink, QuestCompletion, Quest
from django.utils import timezone

def assign_character_to_profile(profile):
    """Utility function to assign a Character to a Profile"""

    PlayerCharacterLink.objects.filter(profile=profile, is_active=True).update(is_active=False)
    
    character = Character.objects.filter(profile__isnull=True, dod__isnull=True).first()

    if character:
         PlayerCharacterLink.objects.create(
              profile=profile,
              character=character,
              is_active=True,
              date_linked=timezone.now().date()
         )

def check_quest_eligibility(character, profile):
    print("Inside check_quest_eligibility")
    char_quests = QuestCompletion.objects.filter(character=character)
    quests_done = {}
    for completion in char_quests:
        quests_done[completion.quest] = completion.times_completed
    
    all_quests = Quest.objects.all()

    eligible_quests = []
    print("Looping through quests now")
    for quest in all_quests:
        print('quest:', quest)
        # Test for eligibility
        if quest.checkEligible(character, profile) and \
            quest.not_repeating(character) and \
            quest.requirements_met(quests_done):
                eligible_quests.append(quest)
                print('success')
    
    return eligible_quests