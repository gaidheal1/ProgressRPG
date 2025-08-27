# gameplay/tests.py

from datetime import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.utils.timezone import now, timedelta
from freezegun import freeze_time
from unittest import skip
import logging

from gameplay.models import (
    Quest,
    QuestRequirement,
    Skill,
    Project,
    QuestCompletion,
    QuestResults,
    Buff,
    AppliedBuff,
    ActivityTimer,
    QuestTimer,
    ServerMessage,
)
from character.models import Character
from progression.models import Activity

logging.getLogger("django").setLevel(logging.CRITICAL)


class TestQuestCreate(TestCase):
    def test_quest_create(self):
        quest = Quest.objects.create(
            name="Test Quest",
            description="Test Quest Description",
            levelMax=10,
        )

        self.assertTrue(isinstance(quest, Quest))
        self.assertEqual(quest.name, "Test Quest")


class TestQuestModels(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.quest1 = Quest.objects.create(
            name="Test Quest",
            description="Test Quest Description",
            levelMax=10,
        )
        cls.quest2 = Quest.objects.create(
            name="Test Quest 2",
            description="Test Quest Description",
            levelMax=10,
        )

    def test_questrequirement_create(self):
        req = QuestRequirement.objects.create(
            quest=self.quest1, prerequisite=self.quest2
        )
        self.assertTrue(isinstance(req, QuestRequirement))
        self.assertEqual(self.quest1, req.quest)
        self.assertEqual(self.quest2, req.prerequisite)

    def test_questcompletion_create(self):
        char = Character.objects.create(name="Bob")
        User = get_user_model()
        user = User.objects.create_user(
            email="testuser1@example.com", password="testpassword123"
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


class TestQuestEligible(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.quest1 = Quest.objects.create(
            name="Test Quest 1",
            description="Test Quest Description 1",
            levelMax=10,
            canRepeat=False,
        )
        cls.quest2 = Quest.objects.create(
            name="Test Quest 2",
            description="Test Quest Description 2",
            levelMax=10,
            canRepeat=True,
            frequency=Quest.Frequency.DAILY,
        )
        cls.quest3 = Quest.objects.create(
            name="Test Quest 3",
            description="Test Quest Description 3",
            levelMax=10,
            canRepeat=False,
        )
        cls.quest4 = Quest.objects.create(
            name="Test Quest 4",
            description="Test Quest Description 4",
            levelMax=10,
            canRepeat=True,
            frequency=Quest.Frequency.DAILY,
        )
        cls.quest5 = Quest.objects.create(
            name="Test Quest 5",
            description="Test Quest Description 5",
            levelMax=10,
            canRepeat=True,
            frequency=Quest.Frequency.WEEKLY,
        )
        cls.quest6 = Quest.objects.create(
            name="Test Quest 6",
            description="Test Quest Description 6",
            levelMax=10,
            canRepeat=True,
            frequency=Quest.Frequency.MONTHLY,
        )
        cls.questslist1 = [
            cls.quest1,
            cls.quest2,
            cls.quest3,
        ]
        cls.questslist2 = [
            cls.quest4,
            cls.quest5,
            cls.quest6,
        ]

        cls.char = Character.objects.create(name="Bob")
        User = get_user_model()
        cls.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword123"
        )
        cls.req = QuestRequirement.objects.create(
            quest=cls.quest2, prerequisite=cls.quest1
        )
        cls.qc1 = QuestCompletion.objects.create(
            character=cls.char,
            quest=cls.quest1,
            times_completed=0,
            last_completed=now(),
        )
        cls.qc2 = QuestCompletion.objects.create(
            character=cls.char,
            quest=cls.quest3,
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
        self.assertTrue(self.quest2.requirements_met(lst) == False)
        self.assertEqual(len(eligible_quests), 2)
        self.assertEqual(eligible_quests[0], self.quest1)

    def test_quest_repeatable(self):
        eligible_quests = []
        for quest in self.questslist1:
            if quest.not_repeating(self.char):
                eligible_quests.append(quest)

        # self.quest1 can't repeat, and character has completed, so should return false
        self.assertTrue(self.quest3.not_repeating(self.char) == False)
        self.assertTrue(self.quest2.not_repeating(self.char))
        self.assertTrue(len(eligible_quests) == 2)
        self.assertTrue(eligible_quests[0].name == "Test Quest 1")


class TestQuestEligibleFrequency(TestCase):
    def setUp(self):
        self.char = Character.objects.create(name="Bob")
        self.quest4 = Quest.objects.create(
            name="Test Quest 4",
            description="Test Quest Description 4",
            levelMax=10,
            canRepeat=True,
            frequency=Quest.Frequency.DAILY,
        )
        self.quest5 = Quest.objects.create(
            name="Test Quest 5",
            description="Test Quest Description 5",
            levelMax=10,
            canRepeat=True,
            frequency=Quest.Frequency.WEEKLY,
        )
        self.quest6 = Quest.objects.create(
            name="Test Quest 6",
            description="Test Quest Description 6",
            levelMax=10,
            canRepeat=True,
            frequency=Quest.Frequency.MONTHLY,
        )

    @skip("Skipping as temporarily broken")
    def test_frequency_eligible(self):
        today = now()
        yesterday = today - timedelta(days=1)
        weekago = today - timedelta(days=7)
        monthago = today - timedelta(days=27)

        qc4 = QuestCompletion.objects.create(
            character=self.char,
            quest=self.quest4,
            times_completed=3,
            last_completed=yesterday,
        )
        qc5 = QuestCompletion.objects.create(
            character=self.char,
            quest=self.quest5,
            times_completed=3,
            last_completed=weekago,
        )
        qc6 = QuestCompletion.objects.create(
            character=self.char,
            quest=self.quest6,
            times_completed=3,
            last_completed=monthago,
        )

        self.assertTrue(self.quest4.frequency_eligible(self.char))
        self.assertTrue(self.quest5.frequency_eligible(self.char))
        self.assertTrue(self.quest6.frequency_eligible(self.char))


class TestQuestResults(TestCase):
    def setUp(self):
        self.char = Character.objects.create(name="Bob", sex="Male")
        User = get_user_model()
        user = User.objects.create_user(
            email="testuser1@example.com", password="testpassword123"
        )
        self.profile = user.profile

        self.quest1 = Quest.objects.create(
            name="Test Quest1",
            description="Test Quest Description 1",
            levelMax=10,
            canRepeat=True,
        )

        self.result1 = QuestResults.objects.filter(quest=self.quest1).first()
        self.result1.coin_reward = 5
        self.result1.dynamic_rewards = {
            "sex": "Female",
        }
        self.result1.save()
        self.quest1.refresh_from_db()
        self.char.quest_timer.change_quest(self.quest1, 10)

        # Add buff later when fully implemented

    @skip("Skipping as temporarily broken ('character has no quest_timer')")
    def test_questresults(self):
        def display(char):
            print(
                "char",
                char.name,
                "| xp: ",
                char.xp,
                "| coins:",
                char.coins,
                "| sex:",
                char.sex,
            )

        # print("before:")
        # display(self.char)

        self.assertEqual(self.char.coins, 0)
        self.assertEqual(self.char.sex, "Male")

        self.char.complete_quest(5)

        # print("after:")
        # display(self.char)

        self.assertEqual(self.char.coins, 5)
        self.assertEqual(self.char.sex, "Female")

        # Add buff test later when fully implemented


class TestQuestCompletionModel(TestCase):
    def test_questcompletion_create(self):
        char = Character.objects.create(name="Bob")
        self.quest1 = Quest.objects.create(
            name="Test Quest 1",
            levelMax=10,
        )
        qc = QuestCompletion.objects.create(
            character=char, quest=self.quest1, times_completed=1, last_completed=now()
        )

        self.assertTrue(isinstance(qc, QuestCompletion))
        self.assertEqual(qc.character, char)
        self.assertEqual(qc.quest, self.quest1)
        # Again, it prints 'None'
        # print(char.quest_completions)


class BaseTimerTest(TestCase):
    def assertTimerReset(self, timer):
        self.assertIsNone(timer.start_time)
        self.assertEqual(timer.status, "empty")
        self.assertEqual(timer.elapsed_time, 0)


class TestActivityTimer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            email="user1@gmail.com", password="test"
        )
        cls.profile = cls.user.profile
        cls.activity = Activity.objects.create(
            profile=cls.profile, name="Test Activity", duration=10
        )

    def setUp(self):
        self.timer = self.profile.activity_timer

    def test_new_activity_sets_state(self):
        self.timer.new_activity("Test activity")
        self.assertIsInstance(self.timer.activity, Activity)
        self.assertEqual(self.timer.status, "waiting")

    def test_start_and_pause(self):
        self.timer.new_activity("Test activity")
        self.timer.start()
        self.assertEqual(self.timer.status, "active")
        self.assertIsNotNone(self.timer.start_time)

        self.timer.pause()
        self.assertEqual(self.timer.status, "paused")
        self.assertIsNone(self.timer.start_time)
        self.assertGreaterEqual(self.timer.elapsed_time, 0)

    def test_reset_clears_activity(self):
        self.timer.new_activity("Test activity")
        self.timer.reset()
        self.assertIsNone(self.timer.activity)
        self.assertEqual(self.timer.status, "empty")

    @skip("Skipping as temporarily broken")
    def test_complete(self):
        self.timer.new_activity("Test activity")
        self.timer.start()
        self.timer.complete()
        # self.assertIsInstance(xp, int)
        # self.assertEqual(self.timer.status, "empty")
        # self.assertIsNone(self.timer.activity)


class TestQuestTimer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.character = Character.objects.create(name="Hero")
        cls.character.save()
        cls.quest = Quest.objects.create(name="Test Quest", levelMax=10)
        User = get_user_model()
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword123"
        )

    def setUp(self):
        self.timer, created = QuestTimer.objects.get_or_create(character=self.character)

    def test_change_quest_sets_state(self):
        self.timer.change_quest(self.quest, duration=300)
        self.assertEqual(self.timer.quest, self.quest)
        self.assertEqual(self.timer.duration, 300)
        self.assertEqual(self.timer.status, "waiting")

    @skip("Skipping as temporarily broken ('character has no active profile link')")
    def test_start_and_complete(self):
        self.timer.change_quest(self.quest, duration=300)
        self.timer.start()
        self.assertEqual(self.timer.status, "active")
        self.timer.complete()
        self.assertEqual(self.timer.status, "completed")
        self.assertIsInstance(xp, int)

    def test_reset_clears_quest(self):
        self.timer.change_quest(self.quest, duration=300)
        self.timer.reset()
        self.assertIsNone(self.timer.quest)
        self.assertEqual(self.timer.status, "empty")
        self.assertEqual(self.timer.elapsed_time, 0)

    @freeze_time("2025-01-01 12:00:00")
    def test_get_remaining_time(self):
        self.timer.change_quest(self.quest, duration=300)
        self.timer.start()
        with freeze_time("2025-01-01 12:05:00"):
            self.assertEqual(self.timer.get_remaining_time(), 0)
            self.assertTrue(self.timer.time_finished())


class QuestSignalTest(TestCase):
    def test_questresult_created_with_quest(self):
        quest = Quest.objects.create(
            name="Signal Test Quest",
            levelMax=10,
        )
        self.assertTrue(QuestResults.objects.filter(quest=quest).exists())


class TestServerMessageModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword123"
        )
        cls.profile = user.profile

    def test_server_message_create(self):
        message = ServerMessage.objects.create(
            group=self.profile.group_name,
            type="notification",
            action="quest_complete",
            data={"quest_id": 1},
            message="Quest completed successfully!",
            is_draft=False,
        )
        self.assertTrue(isinstance(message, ServerMessage))
        self.assertEqual(message.type, "notification")
        self.assertEqual(message.action, "quest_complete")
        self.assertEqual(message.data["quest_id"], 1)
        self.assertFalse(message.is_delivered)

    def test_server_message_mark_delivered(self):
        message = ServerMessage.objects.create(
            group=self.profile.group_name,
            type="notification",
            action="quest_complete",
            data={"quest_id": 1},
            message="Quest completed successfully!",
            is_draft=False,
        )
        message.mark_delivered()
        self.assertTrue(message.is_delivered)


class TestBuffApplication(TestCase):
    def setUp(self):
        self.char = Character.objects.create(name="Bob")
        self.buff = Buff.objects.create(
            name="Test Buff",
            attribute="xp_modifier",
            duration=10,
            amount=1.5,
            buff_type="multiplicative",
        )

    def test_buff_application(self):
        applied_buff = AppliedBuff.objects.create(
            name=self.buff.name,
            attribute=self.buff.attribute,
            duration=self.buff.duration,
            amount=self.buff.amount,
            buff_type=self.buff.buff_type,
        )
        self.char.buffs.add(applied_buff)
        self.assertTrue(applied_buff.is_active())
        self.assertEqual(applied_buff.calc_value(10), 15)
