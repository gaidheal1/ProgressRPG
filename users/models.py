from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    date_of_birth = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.username

class Player(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(max_length=1000, blank=True)
    profile_picture = models.ImageField(upload_to='users/profile_pics/', null=True, blank=True)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    total_time = models.IntegerField(default=0)
    total_activities = models.IntegerField(default=0)

    def __str__(self):
        return 'profile of user ' + self.user.username
    
    def add_xp(self, amount):
        """Add XP and handle level-up logic."""
        self.xp += amount
        while self.xp >= self.get_xp_for_next_level():
            self.level_up()
        self.save()

    def level_up(self):
        """Increase level and reset XP."""
        self.xp -= self.get_xp_for_next_level()
        self.level += 1

    def get_xp_for_next_level(self):
        return 100 * (self.level + 1) if self.level >= 1 else 100

    def add_activity(self, time, num):
        self.total_time += time
        self.total_activities += num