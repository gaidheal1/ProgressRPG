from django.db import models, transaction
from users.models import Person
from django.utils.timezone import now, timedelta
from datetime import datetime
import json

class Quest(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=2000, blank = True)
    duration = models.PositiveIntegerField(default=0)  # Duration in minutes
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    stages = models.JSONField(default=list)

    # Eligibility criteria
    is_premium = models.BooleanField(default=True)
    levelMin = models.IntegerField(default=0)
    levelMax = models.IntegerField(default=0)
    canRepeat = models.BooleanField(default=False)

    class Frequency(models.TextChoices):
        NONE = 'NONE', 'No repeat'
        DAILY = 'DAY', 'Daily'
        WEEKLY = 'WEEK', 'Weekly'
        MONTHLY = 'MONTH', 'Monthly'

    frequency = models.CharField(
        max_length=6,
        choices=Frequency.choices,
        default=Frequency.NONE
    )

    def __str__(self):
        return f"Quest: {self.name}"
    
    def apply_results(self, results, character):
        """
        Apply a list of quest results (key-value pairs) to the character.
        """
        actions = {
            'xp': lambda char, value: char.add_xp(value),  # Call add_xp method
            'coins': lambda char, value: setattr(char, 'coins', char.coins + value),
            'role': lambda char, value: setattr(char, 'role', value),
        }

        for result in results:
            for key, value in result.items():
                handler = actions.get(key)
                if handler:
                    handler(character, value)  # Execute the handler
                else:
                    print(f"Warning: No handler for key '{key}'.")

        character.save()  # Ensure all changes are persisted

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
        completions = self.quest_completions.all()
        # Check repeating
        if self.canRepeat == False:
            for completion in completions:
                if completion.character == character:
                    if completion.times_completed >= 1:
                        return False
        return True

    def frequency_eligible(self, character):
        # Check frequency eligibility
        if self.frequency != 'NONE':            
            today = now()
            completions = self.quest_completions.all()

            for completion in completions:
                if completion.character == character:
                    lastCompleted = completion.last_completed

                    if self.frequency == 'DAY':
                        todayDate = int(today.strftime('%d'))
                        lastCompletedDate = int(lastCompleted.strftime('%d'))    
                        if todayDate == lastCompletedDate:
                            return False
                        
                    elif self.frequency == 'WEEK':
                        dateDiff = today-lastCompleted
                        if dateDiff.days < 7:
                            if today.weekday() >= lastCompletedDate.weekday():
                                return False

                    elif self.frequency == 'MONTH':
                        dateDiff = today-lastCompleted
                        if dateDiff.days < 31:
                            todayDate = int(today.strftime('%d'))
                            lastCompletedDate = int(lastCompleted.strftime('%d'))
                            if todayDate >= lastCompletedDate:
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
    
    

    
class QuestResults(models.Model):
    quest = models.OneToOneField(Quest, on_delete=models.CASCADE, related_name='results')
    dynamic_rewards = models.JSONField(default=dict)
    xp_reward = models.PositiveIntegerField(default=0)
    coin_reward = models.IntegerField(default=0)
    buffs = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Quest results for Quest '{self.quest.id}': {json.dumps(self.rewards, indent=2)}"

    @transaction.atomic
    def apply(self, person):
        """Apply rewards/results to a given character"""
        if self.xp_reward > 0:
            person.add_xp(self.xp_reward)

        if self.coin_reward != 0:
            person.add_coins(self.coin_reward)

        for key, value in self.dynamic_rewards.items():
            if hasattr(person, f"apply_{key}"):
                method = getattr(person, f"apply_{key}")
                method(value)
            elif hasattr(person, key):
                setattr(person, key, getattr(person, key) + value if isinstance(value, (int, float)) else value)

        for buff_data in self.buffs:
            buff = Buff.objects.create(
                name=buff_data['name'],
                duration= timedelta(seconds=buff_data['duration']),
                amount=buff_data['amount'],
                buff_type=buff_data['buff_type'],
                attribute=buff_data['attribute'],
            )
            person.buffs.add(buff)
        person.save()

class QuestRequirement(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name="quest_requirements")
    prerequisite = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name="required_for") 
    times_required = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.prerequisite.name} required {self.times_required} time(s) for {self.quest.name}"


class Activity(models.Model):
    profile = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name="activities")
    name = models.CharField(max_length=255)
    duration = models.PositiveIntegerField(default=0)  # Time spent
    created_at = models.DateTimeField(auto_now_add=True)
    xp_rate = models.FloatField(default=0.2)
    
    class Meta:
        ordering = ['-created_at'] # Most recent activities first

    def addTime(self, num):
        self.duration += num
        self.save()

    def calculate_xp_reward(self, person):
        """
        Calculate XP reward for this activity, considering buffs.
        """
        base_xp = self.duration * self.xp_rate
        final_xp = person.apply_buffs(base_xp, 'xp')
        return final_xp

    def __str__(self):
        return f"activity {self.name}, created {self.created_at}, duration {self.duration}, profile {self.profile.name}"
    

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
    total_quests = models.PositiveIntegerField(default=0)
    current_quest = models.ForeignKey(Quest, on_delete=models.SET_NULL, blank=True, null=True)
    coins = models.PositiveIntegerField(default=0)
    role = models.CharField(max_length=50, default="Ne'er-do-well")
    buffs = models.ManyToManyField('Buff', related_name='characters', blank=True)

    def __str__(self):
        return self.name if self.name else "Unnamed character"
    
    def start_quest(self, quest):
        self.current_quest = quest
        self.save()

    @transaction.atomic
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
        self.total_quests += 1
        # ??? fix when sorting out new rewards
        # self.add_xp(quest.results.xp)
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
            #print(self)

    def stop(self):
        if self.is_running:
            server_elapsed = (now() - self.start_time).total_seconds()
            self.elapsed_time += int(server_elapsed)
            self.is_running = False
            self.start_time = None
            self.save()
            #print(self)

    def reset(self):
        self.elapsed_time = 0
        self.is_running = False
        self.start_time = None
        self.save()

class ActivityTimer(Timer):
    profile = models.ForeignKey('users.profile', on_delete=models.CASCADE, related_name='activity_timer')
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE, related_name='activity_timer', null=True, blank=True)

    def __str__(self):
        return f"ActivityTimer for profile {self.profile.name}: started {self.start_time}, {self.elapsed_time} elapsed"

class QuestTimer(Timer):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='quest_timer')
    duration = models.IntegerField(default=0)

    def get_remaining_time(self):
        if self.is_running:
            elapsed = (now() - self.start_time).total_seconds()
            return max(self.duration - int(elapsed + self.elapsed_time), 0)
        return max(self.duration - self.elapsed_time, 0)
    
    def is_complete(self):
        return self.get_remaining_time() <= 0

    def __str__(self):
        return f"QuestTimer for profile {self.character.name}: duration {self.duration}, started {self.start_time}, {self.elapsed_time} elapsed"
    

class Buff(models.Model):
    BUFF_TYPE_CHOICES = [
        ('additive', 'Additive'),
        ('multiplicative', 'Multiplicative'),
    ]

    name = models.CharField(max_length=100, default="Default buff name")
    attribute = models.CharField(max_length=50, default="Default buff attribute")
    duration = models.PositiveIntegerField(default=0)
    amount = models.FloatField(null=True, blank=True)
    buff_type = models.CharField(max_length=20, choices=BUFF_TYPE_CHOICES, default='additive')
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        """Check if buff is still active."""
        return now() < self.created_at + self.duration
    
    def calc_value(self, total_value):
        if self.is_active():
            if self.buff_type == 'additive':
                total_value += self.amount
            elif self.buff_type == 'multiplicative':
                total_value *= self.amount
        return int(total_value)
    

                    