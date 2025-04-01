# gameplay/tests.py

from datetime import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import now, timedelta
from time import sleep
from unittest import skip

from .models import Quest, QuestRequirement, Activity, Skill, Project, QuestCompletion, QuestResults, Buff, AppliedBuff, ActivityTimer, QuestTimer, DailyStats, GameWorld
from character.models import Character


# Create your tests here.

class TestQuestCreate(TestCase):
    def test_quest_create(self):
        quest = Quest.objects.create(
            name='Test Quest',
            description='Test Quest Description',
            levelMax=10,
        )

        self.assertTrue(isinstance(quest, Quest))
        self.assertEqual(quest.name, 'Test Quest')

class TestQuestModels(TestCase):
    def setUp(self):
        self.quest1 = Quest.objects.create(
            name='Test Quest',
            description='Test Quest Description',
            levelMax=10,
        )
        self.quest2 = Quest.objects.create(
            name='Test Quest 2',
            description='Test Quest Description',
            levelMax=10,
        )

    def test_questrequirement_create(self):
        req = QuestRequirement.objects.create(
            quest=self.quest1,
            prerequisite=self.quest2
        )
        self.assertTrue(isinstance(req, QuestRequirement))
        self.assertEqual(self.quest1, req.quest)
        self.assertEqual(self.quest2, req.prerequisite)

    def test_questcompletion_create(self):
        char = Character.objects.create(
            name="Bob"
        )        
        User = get_user_model()
        user = User.objects.create_user(
            email='testuser1@example.com',
            password='testpassword123'
        )

        qc = QuestCompletion.objects.create(
            character=char,
            quest=self.quest1,
            times_completed=1,
            last_completed=now(),
        )

        self.assertTrue(isinstance(qc, QuestCompletion))
        self.assertEqual(qc.character, char)
        self.assertEqual(qc.quest, self.quest1)

    def test_questresults_create(self):
        qr = QuestResults.objects.create(
            quest=self.quest1,
        )
        self.assertTrue(isinstance(qr, QuestResults))
        self.assertEqual(qr.quest, self.quest1)
        self.assertEqual(qr.xp_rate, 1)

class TestQuestEligible(TestCase):
    def setUp(self):
        self.quest1 = Quest.objects.create(
            name='Test Quest',
            description='Test Quest Description 1',
            levelMax=10,
            canRepeat=False
        )
        self.quest2 = Quest.objects.create(
            name='Test Quest 2',
            description='Test Quest Description 2',
            levelMax=10,
            canRepeat=True,
            frequency=Quest.Frequency.DAILY,
        )
        self.quest3 = Quest.objects.create(
            name='Test Quest 3',
            description='Test Quest Description 3',
            levelMax=10,
            canRepeat=False
        )
        self.quest4 = Quest.objects.create(
            name='Test Quest 4',
            description='Test Quest Description 4',
            levelMax=10,
            canRepeat=True,
            frequency=Quest.Frequency.DAILY,
        )
        self.quest5 = Quest.objects.create(
            name='Test Quest 5',
            description='Test Quest Description 5',
            levelMax=10,
            canRepeat=True,
            frequency=Quest.Frequency.WEEKLY,
        )
        self.quest6 = Quest.objects.create(
            name='Test Quest 6',
            description='Test Quest Description 6',
            levelMax=10,
            canRepeat=True,
            frequency=Quest.Frequency.MONTHLY,
        )
        self.questslist1=[
            self.quest1, 
            self.quest2,
            self.quest3,
            ]

        self.questslist2 = [
            self.quest4,
            self.quest5,
            self.quest6,
        ]
        self.char = Character.objects.create(
            name="Bob"
        )
        User = get_user_model()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123'
        )
        self.req = QuestRequirement.objects.create(
            quest=self.quest2,
            prerequisite=self.quest1
        )
        self.qc1 = QuestCompletion.objects.create(
            character=self.char,
            quest=self.quest1,
            times_completed=0,
            last_completed=now(),
        )
        self.qc2 = QuestCompletion.objects.create(
            character=self.char,
            quest=self.quest3,
            times_completed=1,
            last_completed=now(),
        )

    def test_quest_requirements_met(self):
        lst = {}
        lst[self.qc1.quest] = self.qc1.times_completed
        eligible_quests = []
        for quest in self.questslist1:
            if quest.requirements_met(lst):
                eligible_quests.append(quest)

        self.assertTrue(self.quest1.requirements_met(lst))
        self.assertTrue(self.quest2.requirements_met(lst)== False)
        self.assertEqual(len(eligible_quests), 2)
        self.assertEqual(eligible_quests[0], self.quest1)

    def test_quest_repeatable(self):
        eligible_quests = []
        for quest in self.questslist1:
            if quest.not_repeating(self.char):
                eligible_quests.append(quest)

        # self.quest1 can't repeat, and character has completed, so should return false
        self.assertTrue(self.quest3.not_repeating(self.char)==False)
        self.assertTrue(self.quest2.not_repeating(self.char))
        self.assertTrue(len(eligible_quests)==2)
        self.assertTrue(eligible_quests[0].name == 'Test Quest')

class TestQuestEligibleFrequency(TestCase):
    @skip("Skipping due to being impossible to test!")
    def setUp(self):
        self.quest4 = Quest.objects.create(
            name='Test Quest 4',
            description='Test Quest Description 4',
            levelMax=10,
            canRepeat=True,
            frequency=Quest.Frequency.DAILY,
        )
        self.quest5 = Quest.objects.create(
            name='Test Quest 5',
            description='Test Quest Description 5',
            levelMax=10,
            canRepeat=True,
            frequency=Quest.Frequency.WEEKLY,
        )
        self.quest6 = Quest.objects.create(
            name='Test Quest 6',
            description='Test Quest Description 6',
            levelMax=10,
            canRepeat=True,
            frequency=Quest.Frequency.MONTHLY,
        )

    def test_frequency_eligible(self):
        eligible_quests = []
        for quest in self.questslist2:
            if quest.frequency_eligible(self.char):
                eligible_quests.append(quest)

        self.assertTrue(len(eligible_quests) == 3)

        today = now()
        yesterday = today - timedelta(days=1)
        weekago = today - timedelta(days=7)
        monthago = today - timedelta(days=27)

        qc4 = QuestCompletion.objects.create(
            character=self.char,
            quest=self.quest4,
            times_completed=3,
            last_completed=today,
        )
        qc5 = QuestCompletion.objects.create(
            character=self.char,
            quest=self.quest5,
            times_completed=3,
            last_completed=today,
        )
        qc6 = QuestCompletion.objects.create(
            character=self.char,
            quest=self.quest6,
            times_completed=3,
            last_completed=today,
        )
        self.questslist2 = [
            self.quest4,
            self.quest5,
            self.quest6,
        ]
        self.char = Character.objects.create(
            name="Bob"
        )
        User = get_user_model()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123'
        )

        self.assertTrue(self.quest4.frequency_eligible(self.char)==False)
        qc4.last_completed = yesterday
        qc4.save()
        self.assertTrue(self.quest4.frequency_eligible(self.char))
        self.assertTrue(self.quest5.frequency_eligible(self.char)==False)
        qc5.last_completed = weekago
        qc5.save()
        self.assertTrue(self.quest5.frequency_eligible(self.char))
        self.assertTrue(self.quest6.frequency_eligible(self.char)==False)
        qc6.last_completed = monthago
        qc6.save()
        self.assertTrue(self.quest6.frequency_eligible(self.char))

class TestQuestResults(TestCase):
    def setUp(self):
        self.char = Character.objects.create(
            name="Bob",
            sex="Male"
        )
        User = get_user_model()
        user = User.objects.create_user(
            email='testuser1@example.com',
            password='testpassword123'
        )
        self.profile = user.profile

        self.quest1 = Quest.objects.create(
            name='Test Quest',
            description='Test Quest Description 1',
            levelMax=10,
            canRepeat=True
        )
        self.quest2 = Quest.objects.create(
            name='Test Quest 2',
            description='Test Quest Description 2',
            levelMax=10,
            canRepeat=True,
            frequency='DAY',
        )
        self.result1 = QuestResults.objects.create(
            quest = self.quest1,
            coin_reward = 5,
            dynamic_rewards = {"sex": "Female",}
        )
        self.char.quest_timer.change_quest(self.quest1)

        # Add buff later when fully implemented
        

    def test_questresults(self):
        def display(char):
            print("char", char.name, "| xp: ", char.xp, "| coins:", char.coins, "| sex:", char.sex)
        #print("before:")
        #display(self.char)

        self.assertEqual(self.char.coins, 0)
        self.assertEqual(self.char.sex, "Male")

        self.char.complete_quest()
        #print("after:")
        #display(self.char)

        self.assertEqual(self.char.coins, 5)
        self.assertEqual(self.char.sex, "Female")

        # Add buff test later when fully implemented
    

class TestActivityModel(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user(
            email='testuser1@example.com',
            password='testpassword123'
        )
        self.profile = user.profile
        self.quest1 = Quest.objects.create(
            name='Test Quest 1',
            description='Test Quest Description 1',
            levelMax=10,
            canRepeat=False
        )

    def test_activity_create(self):
        act = Activity.objects.create(
            profile=self.profile,
            name='Writing tests',
            duration=10
        )

        self.assertTrue(isinstance(act, Activity))
        self.assertEqual(act.profile, self.profile)
        self.assertEqual(act.name, 'Writing tests')
        # created_at is 'NoneType', don't know why
        #print(act.created_at)

    def test_activity_func(self):
        act = Activity.objects.create(
            profile=self.profile,
            name='Writing tests',
            duration=10
        )

        act.add_time(5)
        self.assertEqual(act.duration, 15)

        num = act.calculate_xp_reward()
        self.assertEqual(act.calculate_xp_reward(), act.duration * act.xp_rate)

class TestSkillProjectModels(TestCase):
    def setUp(self):
        self.char = Character.objects.create(
            name="Bob",
            sex="Male"
        )
        User = get_user_model()
        user = User.objects.create_user(
            email='testuser1@example.com',
            password='testpassword123'
        )
        self.profile = user.profile

    def test_skill_create(self):
        skill = Skill.objects.create(
            profile=self.profile,
            name="Test Skill",
        )
        self.assertTrue(isinstance(skill, Skill))
        self.assertEqual(skill.name, "Test Skill")

    def test_project_create(self):
        project = Project.objects.create(
            profile=self.profile,
            name="Test Project",
        )
        self.assertTrue(isinstance(project, Project))
        self.assertEqual(project.name, "Test Project")

class TestQuestCompletionModel(TestCase):
    def test_questcompletion_create(self):
        char = Character.objects.create(
            name="Bob"
        )
        self.quest1 = Quest.objects.create(
            name="Test Quest 1",
            levelMax=10,
        )
        qc = QuestCompletion.objects.create(
            character=char,
            quest=self.quest1,
            times_completed=1,
            last_completed=now()
        )

        self.assertTrue(isinstance(qc, QuestCompletion))
        self.assertEqual(qc.character, char)
        self.assertEqual(qc.quest, self.quest1)
        # Again, it prints 'None'
        #print(char.quest_completions)

class TestBuffModel(TestCase):
    def test_buff_create(self):
        buff1 = Buff.objects.create(
            name = "Buff 1",
            attribute = "xp_modifier",
            duration = 100,
            amount = 1,
            buff_type = 'additive',
        )

        self.assertEqual(buff1.name, "Buff 1")

        appliedbuff1 = AppliedBuff.objects.create(
            name = buff1.name,
            attribute = buff1.attribute,
            duration = buff1.duration,
            amount = buff1.amount,
            buff_type = buff1.buff_type,
        )
        self.assertTrue(appliedbuff1.is_active)
        self.assertTrue(appliedbuff1.calc_value(1), 2)

        buff2 = Buff.objects.create(
            name = "Buff 2",
            attribute = "xp_modifier",
            duration = 10,
            amount = 1.1,
            buff_type = 'multiplicative',
        )
        self.assertEqual(buff2.name, "Buff 2")
        appliedbuff2 = AppliedBuff.objects.create(
            name = buff2.name,
            attribute = buff2.attribute,
            duration = buff2.duration,
            amount = buff2.amount,
            buff_type = buff2.buff_type,
        )
        self.assertTrue(appliedbuff2.calc_value(1), 1.1)
        self.assertTrue(appliedbuff2.is_active())
        # Make buff start time old enough to be expired already
        test = timedelta(seconds=50)
        appliedbuff2.applied_at -= test
        self.assertTrue(appliedbuff2.is_active() == False)

    def test_questresults_create(self):
        quest = Quest.objects.create(
            name='Testing Quest Completion'
        )
        buff1 = Buff.objects.create(
            name = "Buff 1",
            attribute = "xp_modifier",
            duration = 100,
            amount = 1,
            buff_type = 'additive',
        )
        result1 = QuestResults.objects.create(
            quest = quest,
            dynamic_rewards = {},
            coin_reward = 5,
            buffs = ["buff1"],
        )

        #print(result1)

class TestTimers(TestCase):
    def setUp(self):
        self.char = Character.objects.create(
            name="Bob"
        )
        quest_timer = QuestTimer.objects.create(character=self.char)
        User = get_user_model()
        user = User.objects.create_user(
            email='testuser1@example.com',
            password='testpassword123'
        )
        self.profile = user.profile
        self.quest1 = Quest.objects.create(
            name='Test Quest 1',
            description='Test Quest Description 1',
            levelMax=10,
            canRepeat=False
        )
        self.act = Activity.objects.create(
            profile=self.profile,
            name='Writing tests',
            duration=10
        )
        self.quest1 = Quest.objects.create(
            name='Test Quest 1',
            description='Test Quest Description 1',
            levelMax=10,
            canRepeat=False
        )

    def test_timer_create(self):
        activity_timer = ActivityTimer.objects.filter(profile = self.profile).first()
        self.assertTrue(isinstance(activity_timer, ActivityTimer))
        self.assertEqual(activity_timer.profile, self.profile)

        quest_timer = QuestTimer.objects.filter(character = self.char).first()
        self.assertTrue(isinstance(quest_timer, QuestTimer))
        self.assertEqual(quest_timer.character, self.char)

    def test_timer_start(self):
        timer = ActivityTimer.objects.filter(profile = self.profile).first()
        self.assertTrue(timer.start_time == None)
        self.assertEqual(timer.status, "empty")

        timer.start()

        self.assertTrue(timer.start_time)
        self.assertEqual(timer.status, "active")

    def test_timer_pause(self):
        timer = ActivityTimer.objects.filter(profile = self.profile).first()
        timer.start()
        timer.pause()

        self.assertTrue(timer.start_time == None)
        self.assertEqual(timer.status, "paused")
        # Need to wait for couple secs before next test as it is integerised in Timer method
        #self.assertTrue(timer.elapsed_time > 0)

    def test_timer_reset(self):
        timer = ActivityTimer.objects.filter(profile = self.profile).first()
        timer.start()
        timer.new_activity(self.act)
        timer.complete()
        timer.reset()

        self.assertTrue(timer.start_time == None)
        self.assertEqual(timer.status, "empty")
        self.assertTrue(timer.elapsed_time == 0)

    def test_questtimer_func(self):        
        timer = QuestTimer.objects.filter(character = self.char).first()
        timer.duration = 5
        timer.start()

        self.assertTrue(timer.get_remaining_time() > 0)
        self.assertTrue(timer.is_complete() == False)

class TestDailyStats(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user(
            email='testuser1@example.com',
            password='testpassword123'
        )
        self.profile = user.profile

        self.stat = DailyStats.objects.create(
            recordDate = now().date(),
        )
        self.stat.save()

    def test_dailystats_create(self):
        stat = DailyStats.objects.create(
            recordDate = now().date(),
        )
        stat.save()
        
        self.assertTrue(isinstance(stat, DailyStats))
        self.assertTrue(stat.newUsers == 0)

    def test_dailystats_func(self):
        today = now().date()
        

        dailystat = DailyStats.objects.get(recordDate=today)
        print("dailystat:", dailystat)
        
class TestStatsView(TestCase):
    @skip("Skipping due to DB changes")
    def setUp(self):
        self.client = Client()

        # urls
        self.index_url = reverse('index')
        self.profile_url = reverse('profile')
        self.editprofile_url = reverse('edit_profile')
        self.statistics_url = reverse('get_game_statistics')
        User = get_user_model()
        user1 = User.objects.create_user(
            email='testuser1@example.com',
            password='testpassword123'
        )
        user2 = User.objects.create_user(
            email='testuser2@example.com',
            password='testpassword123'
        )

        self.client.login(email='testuser1@example.com', password='testpassword123')

        self.profile1 = user1.profile
        self.activity = Activity.objects.create(
            profile=self.profile1,
            name='Writing tests',
            duration=10
        )
        self.profile2 = user2.profile
        self.activity = Activity.objects.create(
            profile=self.profile2,
            name='Writing tests',
            duration=10
        )

        self.quest1 = Quest.objects.create(
            name='Test Quest 1',
            description='Test Quest Description 1',
            levelMax=10,
            canRepeat=True,
        )

        self.quest2 = Quest.objects.create(
            name='Test Quest 2',
            description='Test Quest Description 2',
            levelMax=10,
            canRepeat=False,
        )
        self.char1 = Character.objects.create(
            profile=self.profile1,
            name="Bob"
        )

        qc1 = QuestCompletion.objects.create(
            character=self.char1,
            quest=self.quest1,
            times_completed=1,
            last_completed=now(),
        )

        self.char2 = Character.objects.create(
            profile=self.profile2,
            name="Bob"
        )

        qc2 = QuestCompletion.objects.create(
            character=self.char2,
            quest=self.quest1,
            times_completed=5,
            last_completed=now(),
        )

        qc2 = QuestCompletion.objects.create(
            character=self.char2,
            quest=self.quest2,
            times_completed=1,
            last_completed=now(),
        )
    def test_statistics_GET(self):
        response = self.client.get(self.statistics_url)
        #self.assertEqual(response.status_code, 200)
        #self.assertTemplateUsed(response, 'users/index.html')

class TestGameWorld(TestCase):


    def test_gameworld_create(self):
        gw = GameWorld.objects.create()
        today = now()
        tomorrow = today + timedelta(days=1)

        print(gw)
        self.assertTrue(isinstance(gw, GameWorld))