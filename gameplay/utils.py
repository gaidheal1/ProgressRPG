from .models import QuestCompletion, Quest, ActivityTimer, QuestTimer
from character.models import Character, PlayerCharacterLink
from django.utils.timezone import now
import logging

logger = logging.getLogger("django")  # Get the logger for this module

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

def start_timers(profile):
    character = PlayerCharacterLink().get_character(profile)
    logger.info("[START TIMERS] reached")
    logger.debug(f"activity status: {profile.activity_timer.status}, quest status: {character.quest_timer.status}")
    print(f"activity status: {profile.activity_timer.status}, quest status: {character.quest_timer.status}")
    #character.quest_timer = QuestTimer.objects.get(id=character.quest_timer.id)
    if profile.activity_timer.status in ['paused', 'waiting'] and character.quest_timer.status in ['paused', 'waiting']:
        profile.activity_timer.start()
        #character.quest_timer.refresh_from_db()
        print("Before timer start:", character.quest_timer)
        print(f"{now()} - start_timers")
        character.quest_timer.start()
        print("After timer start:", character.quest_timer)
        return "start_timers"
    return ""




def log_timer(label, timer):
    """
    Logs the status of a timer with a given label.
    
    :param label: Descriptive label for the log message
    :param timer: Timer object with a status attribute
    """
    logger.debug(f"[{label}] Timer Status: {timer.status}")
