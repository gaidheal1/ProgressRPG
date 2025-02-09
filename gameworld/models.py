# gameworld.models

from django.db import models
from django.utils import timezone
from random import random


class WeatherType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    min_temp_change = models.IntegerField()
    max_temp_change = models.IntegerField()
    typical_duration = models.IntegerField(default=3) # default duration in days
    crop_growth_modifier = models.FloatField(default=1.0)
    travel_speed_modifier = models.FloatField(default=1.0)
    cleanliness_modifier = models.FloatField(default=1.0)

    def __str__(self):
        return self.name

class WeatherEvent(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    weather_type = models.ForeignKey('WeatherType', on_delete=models.SET_NULL, null=True)
    base_temperature = models.IntegerField()
    location = models.ForeignKey("locations.Location", on_delete=models.CASCADE)

    def generate_daily_temperatures(self):
        num_days = (self.end_date - self.start_date).days
        temperatures = [self.base_temperature]

        for _ in range(num_days - 1):
            change = random.randint(self.weather_type.min_temperature_change, self.weather_type.max_temperature_change)
            new_temp = max(min(temperatures[-1] + change, 40), -10)
            temperatures.append(new_temp)

        return temperatures
    def __str__(self):
        return f"{self.weather_type.name} ({self.start_date} - {self.end_date})"

class Weather(models.Model):
    SEASONS = ["Spring", "Summer", "Autumn", "Winter"]

    BASE_TEMPERATURES = {
        "Spring": (10, 20),
        "Summer": (15, 30),
        "Autumn": (5, 15),
        "Winter": (-5, 5),
    }

    date = models.DateField()
    season = models.CharField(max_length=6, choices=[(s, s) for s in SEASONS])
    weather_event = models.ForeignKey('WeatherEvent', on_delete=models.CASCADE)
    temperature = models.IntegerField()
    crop_growth_modifier = models.FloatField(default=1.0)
    travel_speed_modifier = models.FloatField(default=1.0)
    cleanliness_modifier = models.FloatField(default=1.0)

    def get_season(self):
        month = self.date.month
        if month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        elif month in [9, 10, 11]:
            return "Autumn"
        elif month in [12, 1, 2]:
            return "Winter"

    @classmethod
    def generate_weather_forecast(cls, start_date=None, days_ahead=30):
        if not start_date:
            start_date = timezone.now().date()

        end_date = start_date + timezone.timedelta(days=days_ahead)
        current_date = start_date

        while current_date < end_date:
            # check if there's already a weather event covering this day
            existing_event = WeatherEvent.objects.filter(start_date__lte=current_date, end_date__gte=current_date).first()

            if not existing_event:
                weather_type = random.choice(WeatherType.objects.all())
                duration = random.randint(2, weather_type.typical_duration + 2)
                end_event_date = current_date + timezone.timedelta(days=duration - 1)
                min_temp, max_temp = cls.BASE_TEMPERATURES[cls.season]
                base_temp = random.randint(min_temp, max_temp)

                event = WeatherEvent.objects.create(
                    start_date=current_date,
                    end_date=end_event_date,
                    weather_type=weather_type,
                    base_temperature=base_temp
                )

            else:
                event = existing_event

            temperatures = event.generate_daily_temperatures()
            for i in range(len(temperatures)):
                weather_date = event.start_date + timezone.timedelta(days=i)
                if weather_date >= end_date:
                    break

                Weather.objects.create(
                    date=weather_date,
                    weather_event=event,
                    temperature=temperatures[i]
                )

            current_date = event.end_date + timezone.timedelta(days=1)  # Move past this event

    @classmethod
    def get_forecast(cls, days_ahead=7):
        """Retrieve the weather forecast for the next X days"""
        today = timezone.now().date()
        return cls.objects.filter(date__gte=today, date__lte=today + timezone.timedelta(days=days_ahead))

    def get_temperature(self):
        min_temp, max_temp = self.BASE_TEMPERATURES[self.season]
        temperature_change = random.randint(self.weather_type.min_temperature_change, self.weather_type.max_temperature_change)
        new_temp = random.randint(min_temp, max_temp) + temperature_change
        return new_temp

    def update_weather(self):
        self.season = self.get_season()
        self.weather_type = self.get_weather_type()
        self.temperature = self.get_temperature()
        self.crop_growth_modifier = self.weather_type.crop_growth_modifier
        self.travel_speed_modifier = self.weather_type.travel_speed_modifier
        self.cleanliness_modifier = self.weather_type.cleanliness_modifier

    def save(self, *args, **kwargs):
        self.season = self.get_season()
        super().save(*args, **kwargs)














