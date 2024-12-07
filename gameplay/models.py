from django.db import models, transaction
from users.models import Person
from django.utils.timezone import now

class Quest(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=2000, blank = True)
    duration = models.PositiveIntegerField(default=0)  # Duration in minutes
    number_stages = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    is_premium = models.BooleanField(default=True)
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
        #print("you have arrived in requirements_met")
        for requirement in self.quest_requirements.all():
            completed_count = completed_quests.get(requirement.prerequisite, 0)
            if completed_count < requirement.times_required:
                return False
        return True
    
    def not_repeating(self, character):
        #print("you have arrived in not_repeating")
        if self.canRepeat == False:
            for completion in self.quest_completions.all():
                if completion.character == character:
                    if completion.times_completed >= 1:
                        return False
        return True
    
    def checkEligible(self, character, profile):
        #print("you have arrived in checkEligible")
        #Simple comparison checks
        if character.level < self.levelMin or \
            character.level > self.levelMax:
            return False
        elif profile.is_premium and self.is_premium:
            return False
        # Quest passed the test
        return True
    
class QuestStage(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='quest_stages')
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
    
class Character(Person):
    profile = models.ForeignKey('users.profile', on_delete=models.CASCADE, related_name='character')
    quest_completions = models.ManyToManyField('gameplay.Quest', through='QuestCompletion', related_name='completed_by')
    current_quest = models.ForeignKey(Quest, on_delete=models.SET_NULL, blank=True, null=True)
    coins = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name if self.name else "Unnamed character"
    
    def start_quest(self, quest):
        self.current_quest = quest
        self.save()

    def complete_quest(self):
        if not self.current_quest:
            raise ValueError("No active quest.")
        
        with transaction.atomic():
            completion, created = QuestCompletion.objects.get_or_create(
                character=self,
                quest=self.current_quest
            )
            if not created:
                completion.times_completed += 1
                completion.save()
        self.current_quest = None
        self.save()

class QuestCompletion(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    quest = models.ForeignKey('gameplay.Quest', on_delete=models.CASCADE, related_name='quest_completions')
    times_completed = models.PositiveIntegerField(default=1)
    last_completed = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"character {self.character.name} has done quest {self.quest.name} {self.times_completed} times"

class Timer(models.Model):
    start_time = models.DateTimeField(null=True, blank=True)
    elapsed_time = models.IntegerField(default=0)  # Time in seconds
    is_running = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def start(self):
        if not self.is_running:
            self.start_time = now()
            self.is_running = True
            self.save()

    def stop(self):
        if self.is_running:
            server_elapsed = (now() - self.start_time).total_seconds()
            self.elapsed_time += int(server_elapsed)
            self.is_running = False
            self.start_time = None
            self.save()

    def reset(self):
        self.elapsed_time = 0
        self.is_running = False
        self.start_time = None
        self.save()

class ActivityTimer(Timer):
    profile = models.OneToOneField('users.profile', on_delete=models.CASCADE, related_name='activity_timer')

class QuestTimer(Timer):
    character = models.OneToOneField(Character, on_delete=models.CASCADE, related_name='quest_timer')
    duration = models.IntegerField()

    def get_remaining_time(self):
        if self.is_running:
            elapsed = (now() - self.start_time).total_seconds()
            return max(self.duration - int(elapsed + self.elapsed_time), 0)
        return max(self.duration - self.elapsed_time, 0)
    
    def is_complete(self):
        return self.get_remaining_time() <= 0
