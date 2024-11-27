from django.db import models


class Quest(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=2000, blank = True)
    duration = models.PositiveIntegerField(default=0)  # Duration in minutes
    number_stages = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    levelMin = models.IntegerField(default=0)
    levelMax = models.IntegerField(default=0)
    canRepeat = models.BooleanField(default=False)
    xpReward = models.IntegerField(default=0)
    # need to add requirement(s) for other quests

    def __str__(self):
        return f"Quest: {self.name}"
    
    def requirements_met(self, completed_quests):
        """
        Check if all requirements are satisfied based on completed quests.
        
        :param completed_quests: A dictionary {quest_id: completion_count}.
        :return: True if all requirements are met, False otherwise.
        """
        for requirement in self.quest_requirements.all():
            completed_count = completed_quests.get(requirement.prerequisite.id, 0)
            if completed_count < requirement.times_required:
                return False
        return True
    
class QuestStage(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    stage_num = models.IntegerField(default=0)
    stage_time = models.IntegerField(default=0)
    stage_text = models.TextField(default="Stage default text")

class QuestRequirement(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name="quest_requirements")
    prerequisite = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name="required_for") 
    times_required = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.prerequisite.name} required {self.times_required} time(s) for {self.quest.name}"


class Activity(models.Model):
    profile = models.ForeignKey('users.profile', on_delete=models.CASCADE, related_name="activities")
    #quest = models.ForeignKey(Quest, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    duration = models.PositiveIntegerField(default=0)  # Time spent
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

        if self.profile:
            self.profile.add_activity(self.duration, 1)
            self.profile.save()

        """ if self.skill:
            self.skill.time += self.time
            self.skill.save() """

class Skill(models.Model):
    profile = models.ForeignKey('users.profile', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    time = models.PositiveIntegerField(default=0)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    

class Character(models.Model):
    profile = models.ForeignKey('users.profile', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quest_completions = models.ManyToManyField('gameplay.Quest', through='QuestCompletion', related_name='completed_by')

class QuestCompletion(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    quest = models.ForeignKey('gameplay.Quest', on_delete=models.CASCADE)
    times_completed = models.PositiveIntegerField(default=0)
    