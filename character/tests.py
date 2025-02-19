from django.test import TestCase
from .models import Character, PlayerCharacterLink
from gameplay.models import QuestCompletion, Quest, QuestTimer

# Create your tests here.



class TestCharacterCreate(TestCase):
    def test_character_create(self):
        char = Character.objects.create(
            first_name="Bob"
        )

        self.assertTrue(isinstance(char, Character))
        self.assertEqual(char.first_name, 'Bob')

class TestCharacterMethods(TestCase):
    def setUp(self):
        self.char = Character.objects.create(
            first_name="Bob",
            last_name="Bobberson",
        )
        self.quest1 = Quest.objects.create(
            name="Test Quest 1",
            levelMax=10,
        )
        self.timer = QuestTimer.objects.create(
            character=self.char,
            quest=self.quest1,
            duration=10,
            elapsed_time=5,
        )

    def test_character_properties(self):
        self.assertEqual(self.char.full_name, "Bob Bobberson")

    def test_start_quest(self):
        self.char.start_quest(self.quest1)
        self.assertEqual(self.timer.quest, self.quest1)

    def test_complete_quest(self):
        self.char.complete_quest(self.quest1)
        self.assertEqual(self.char.total_quests, 1)
        completion = QuestCompletion.objects.filter(
            character=self.char,
            quest=self.quest1,
        ).first()
        self.assertEqual(completion.times_completed, 1)

        completions = self.char.get_quest_completions(self.quest1)
        self.assertEqual(completion, completions[0])

class TestPlayerCharacterLinkCreate(TestCase):
    def setUp(self):
        self.char = Character.objects.create(
            first_name="Bob"
        )

    def test_link_create(self):
        #link = PlayerCharacterLink.objects.create(
        #    profile=self.profile,
        #    character=self.char,
        #)
        pass

class TestPlayerCharacterLinkMethods(TestCase):
    def setUp(self):
        self.char = Character.objects.create(
            first_name="Bob"
        )
        #self.link = PlayerCharacterLink.objects.create(
        #    profile=self.profile,
        #    character=self.char,
        #)

    def test_link_func(self):
        pass





