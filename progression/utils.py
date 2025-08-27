from .models import CharacterQuest

from character.models import Character
from gameplay.models import Quest


def copy_quest(character: Character, quest: Quest):
    """
    Create a CharacterQuest instance from a Quest for a given character.

    Copies narrative fields (intro/outro), description, stages, and stage
    behaviour.
    """
    return CharacterQuest.objects.create(
        character=character,
        name=quest.name,
        description=quest.description,
        intro_text=quest.intro_text,
        outro_text=quest.outro_text,
        stages=quest.stages,
        stagesFixed=quest.stagesFixed,
        # Player chooses duration later; leave at default
        quest_duration=0,
        duration=0,
    )
