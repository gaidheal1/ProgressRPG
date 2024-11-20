from django.db import models
from users.models import CustomUser, Player

class Quest(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.PositiveIntegerField()  # Duration in minutes
    created_at = models.DateTimeField(auto_now_add=True)

class Activity(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="activities")
    #quest = models.ForeignKey(Quest, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    duration = models.PositiveIntegerField()  # Time spent
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # Most recent activities first
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Add the activity duration to the skill's total_time when saving the activity
        if self.pk:
            old_activity = Activity.objects.get(pk=self.pk)
            if old_activity.skill:
                old_activity.skill.time -= old_activity.time
                old_activity.skill.save()

        if self.user:
            self.user.profile.add_activity(self.time, 1)
            self.user.profile.save()

        if self.skill:
            self.skill.time += self.time
            self.skill.save()

class Skill(models.Model):
    player = models.ForeignKey('users.Player', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    time = models.PositiveIntegerField(default=0)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    

