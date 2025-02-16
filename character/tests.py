from django.test import TestCase

# Create your tests here.



class TestCharacter(TestCase):
    def test_character_create(self):
        char = Character.objects.create(
            profile=self.profile,
            name="Bob"
        )

        self.assertTrue(isinstance(char, Character))
        self.assertEqual(char.profile, self.profile)
        self.assertEqual(char.name, 'Bob')

    def test_character_func(self):
        char = Character.objects.create(
            profile=self.profile,
            name="Bob",
            current_quest = self.quest1,
        )

        char.complete_quest()
        completion = QuestCompletion.objects.get(
                character=char
        )
        self.assertEqual(completion.times_completed, 1)
        self.assertEqual(char.current_quest, None)
        self.assertEqual(char.total_quests, 1)