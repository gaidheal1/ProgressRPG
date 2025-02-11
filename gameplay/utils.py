from .models import QuestCompletion, Quest
from character.models import Character, PlayerCharacterLink



def check_quest_eligibility(character, profile):
    char_quests = QuestCompletion.objects.filter(character=character)
    quests_done = {}
    for completion in char_quests:
        quests_done[completion.quest] = completion.times_completed
    
    all_quests = Quest.objects.all()

    eligible_quests = []
    for quest in all_quests:
        #print('quest:', quest)
        # Test for eligibility
        if quest.checkEligible(character, profile) and \
            quest.not_repeating(character) and \
            quest.requirements_met(quests_done):
                eligible_quests.append(quest)
                print('success')
    
    return eligible_quests