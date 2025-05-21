from datetime import datetime, date
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, Client
from django.utils import timezone
from django.utils.timezone import now, timedelta
from unittest import skip

from .models import WeatherType, WeatherEvent, Weather, GameWorld, DailyStats, Season

from gameplay.models import Quest, QuestCompletion, Activity
from character.models import Character


class TestWeatherType(TestCase):
    def test_weathertype_create(self):
        wt = WeatherType.objects.create(
            name="Rain",
            min_temp_change=3,
            max_temp_change=10,
        )
        self.assertTrue(isinstance(wt, WeatherType))
        self.assertEqual(wt.name, "Rain")

class TestWeatherEvent(TestCase):
    def setUp(self):
        self.wt = WeatherType.objects.create(
            name="Rain",
            min_temp_change=3,
            max_temp_change=10,
        )

    def test_weatherevent_create(self):
        td = timedelta(days=1)
        we = WeatherEvent.objects.create(
            start=now(),
            end=now()+td,
            weather_type=self.wt,
            base_temperature=10,
        )

        self.assertTrue(isinstance(we, WeatherEvent))
        self.assertEqual(we.start.date(), now().date())

class TestWeather(TestCase):
    def setUp(self):
        self.wt1 = WeatherType.objects.create(
            name="Rain",
            min_temp_change=1,
            max_temp_change=5,
            typical_duration=1,
        )
        self.wt2 = WeatherType.objects.create(
            name="Sun",
            min_temp_change=3,
            max_temp_change=10,
            typical_duration=1,
        )
        self.gw = GameWorld.objects.create(
            name="Test game world",
            years_diff=-550,
        )
        start = timezone.make_aware(datetime.combine(date(year=1475, month=3, day=1), datetime.min.time()))
        end = timezone.make_aware(datetime.combine(date(year=1475, month=5, day=31), datetime.min.time()))
        self.season = Season.objects.create(
            name="Spring", #Season.SEASON_CHOICES.Spring,
            start_date=start,
            end_date=end,
            year=1475,
        )

    def test_weather(self):
        print(f"Season name: {self.season.name}, start {self.season.start_date}")
        Weather.generate_weather_forecast(self.gw, days_ahead=15)
        #for w in Weather.objects.all():
        #    print(w.display())
        for e in WeatherEvent.objects.all():
            print(e.display())

        #print("And now for the weather...")
        #weathers = Weather.get_forecast(self.gw)
        #for w in weathers:
        #    print(w.display())

        print("Tomorrow's temperatures are:")
        tomorrow = (now().date()) + timedelta(days=1)
        print(Weather.get_hourly_temperatures(tomorrow))
        print("Highs and lows:")
        print(Weather.get_high_and_low(tomorrow))
        print("And tomorrow's tomorrow's temperatures are:")
        tomorrow = tomorrow + timedelta(days=1)
        print(Weather.get_hourly_temperatures(tomorrow))
        print("Highs and lows:")
        print(Weather.get_high_and_low(tomorrow))




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



        