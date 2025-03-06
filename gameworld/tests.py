from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import now, timedelta
from datetime import datetime, date
from .models import WeatherType, WeatherEvent, Weather, GameWorld, Season


# Create your tests here.

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






        