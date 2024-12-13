from django.test import TestCase
from .models import Quest, QuestStage, QuestRequirement, Activity, Character, QuestCompletion
from django.contrib.auth import get_user_model

# Create your tests here.

class TestQuestCreate(TestCase):
    def test_quest_create(self):
        quest = Quest.objects.create(
            name='Test Quest',
            description='Test Quest Description',
            duration=10,
            levelMax=10,
            xpReward=100
        )

        self.assertTrue(isinstance(quest, Quest))
        self.assertEqual(quest.name, 'Test Quest')

class TestQuestOther(TestCase):
    def setUp(self):
        
        self.quest = Quest.objects.create(
            name='Test Quest',
            description='Test Quest Description',
            duration=10,
            levelMax=10,
            xpReward=100
        )
        self.quest2 = Quest.objects.create(
            name='Test Quest 2',
            description='Test Quest Description',
            duration=10,
            levelMax=10,
            xpReward=100
        )

    def test_queststage_create(self):
        stage = QuestStage.objects.create(
            quest=self.quest,
            stage_text="Character is doing something"
        )
        self.assertTrue(isinstance(stage, QuestStage))
        self.assertEqual(self.quest, stage.quest)

    def test_questrequirement_create(self):
        req = QuestRequirement.objects.create(
            quest=self.quest,
            prerequisite=self.quest2
        )
        self.assertTrue(isinstance(req, QuestRequirement))
        self.assertEqual(self.quest, req.quest)
        self.assertEqual(self.quest2, req.prerequisite)

    def test_questcompletion_create(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='testuser1',
            email='testuser1@example.com',
            password='testpassword123'
        )

        char = Character.objects.create(
            profile=user.profile,
            name="Bob"
        )

        qc = QuestCompletion.objects.create(
            character=char,
            quest=self.quest,
            times_completed=1
        )

        self.assertTrue(isinstance(qc, QuestCompletion))
        self.assertEqual(qc.character, char)
        self.assertEqual(qc.quest, self.quest)

class TestQuestFunc(TestCase):
    def setUp(self):
        self.quest = Quest.objects.create(
            name='Test Quest',
            description='Test Quest Description',
            duration=10,
            levelMax=10,
            xpReward=100,
            canRepeat=False
        )
        self.quest2 = Quest.objects.create(
            name='Test Quest 2',
            description='Test Quest Description',
            duration=10,
            levelMax=10,
            xpReward=100,
            canRepeat=True,
            frequency='DAY',
        )
        self.quest3 = Quest.objects.create(
            name='Test Quest 3',
            description='Test Quest Description',
            duration=10,
            levelMax=10,
            xpReward=100,
            canRepeat=False
        )
        self.quest4 = Quest.objects.create(
            name='Test Quest 4',
            description='Test Quest Description',
            duration=10,
            levelMax=10,
            xpReward=100,
            canRepeat=True,
            frequency='MONTH',
        )
        self.quests=[
            self.quest, 
            self.quest2,
            self.quest3,
            self.quest4,
            ]

        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )

        self.char = Character.objects.create(
            profile=self.user.profile,
            name="Bob"
        )

        self.req = QuestRequirement.objects.create(
            quest=self.quest2,
            prerequisite=self.quest
        )

        self.qc1 = QuestCompletion.objects.create(
            character=self.char,
            quest=self.quest,
            times_completed=0
        )
        
        self.qc2 = QuestCompletion.objects.create(
            character=self.char,
            quest=self.quest3,
            times_completed=1
        )

        self.qc3 = QuestCompletion.objects.create(
            character=self.char,
            quest=self.quest4,
            times_completed=3,
        )

    def test_quest_requirements_met(self):
        lst = {}
        lst[self.qc1.quest] = self.qc1.times_completed
        eligible_quests = []
        for quest in self.quests:
            if quest.requirements_met(lst):
                eligible_quests.append(quest)

        self.assertTrue(self.quest.requirements_met(lst))
        self.assertTrue(self.quest2.requirements_met(lst)== False)
        self.assertEqual(len(eligible_quests), 3)
        self.assertEqual(eligible_quests[0], self.quest)

    def test_quest_repeatable(self):
        eligible_quests = []
        for quest in self.quests:
            if quest.not_repeating(self.char):
                eligible_quests.append(quest)

        # self.quest can't repeat, and character has completed, so should return false
        self.assertTrue(self.quest3.not_repeating(self.char)==False)
        self.assertTrue(self.quest2.not_repeating(self.char))
        self.assertTrue(len(eligible_quests)==3)
        self.assertTrue(eligible_quests[0].name == 'Test Quest')

    def test_frequency_eligible(self):
        eligible_quests = []
        for quest in self.quests:
            if quest.frequency_eligible(self.char):
                eligible_quests.append(quest)

        #self.assertTrue(self.quest4.frequency_eligible(self.char)==False)
        

    
    
class TestOtherModels(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser1',
            email='testuser1@example.com',
            password='testpassword123'
        )

    def test_activity_create(self):
        act = Activity.objects.create(
            profile=self.user.profile,
            name='Writing tests',
            duration=10
        )

        self.assertTrue(isinstance(act, Activity))
        self.assertEqual(act.profile, self.user.profile)
        self.assertEqual(act.name, 'Writing tests')
        # created_at is 'NoneType', don't know why
        #print(act.created_at)

    def test_character_create(self):
        char = Character.objects.create(
            profile=self.user.profile,
            name="Bob"
        )

        self.assertTrue(isinstance(char, Character))
        self.assertEqual(char.profile, self.user.profile)
        self.assertEqual(char.name, 'Bob')

    def test_questcompletion_create(self):
        char = Character.objects.create(
            profile=self.user.profile,
            name="Bob"
        )
        quest = Quest.objects.create(
            name='Testing Quest Completion'
        )
        qc = QuestCompletion.objects.create(
            character=char,
            quest=quest,
            times_completed=1
        )

        self.assertTrue(isinstance(qc, QuestCompletion))
        self.assertEqual(qc.character, char)
        self.assertEqual(qc.quest, quest)
        # Again, it prints 'None'
        #print(char.quest_completions)

        