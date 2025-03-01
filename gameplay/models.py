from django.db import models, transaction
from users.models import Person, Profile
from django.utils.timezone import now, timedelta
from datetime import datetime
import json, math, logging
import traceback
from random import random

logger = logging.getLogger("django")

class Quest(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=2000, blank = True)
    intro_text = models.TextField(max_length=2000, blank = True)
    outro_text = models.TextField(max_length=2000, blank = True)
    DURATION_CHOICES = [(300 * i, f"{5 * i} minutes") for i in range(1, 7)]
    def default_duration_choices():
        return [(300 * i, f"{5 * i} minutes") for i in range(1, 7)]
    duration_choices = models.JSONField(default=default_duration_choices)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    stages = models.JSONField(default=list)

    class Category(models.TextChoices):
        NONE = 'NONE', 'No category'
        TRADE = 'TRADE', 'Trade'
        RECUR = 'RECUR', 'Recurring'
        EVENT = 'EVENT', 'Event'

    category = models.CharField(max_length=20, default=Category.NONE)

    # Eligibility criteria
    is_premium = models.BooleanField(default=True)
    levelMin = models.IntegerField(default=0)
    levelMax = models.IntegerField(default=0)
    canRepeat = models.BooleanField(default=False)

    class Frequency(models.TextChoices):
        NONE = 'NONE', 'No limit'
        DAILY = 'DAY', 'Daily'
        WEEKLY = 'WEEK', 'Weekly'
        MONTHLY = 'MONTH', 'Monthly'

    frequency = models.CharField(
        max_length=6,
        choices=Frequency.choices,
        default=Frequency.NONE
    )

    def __str__(self):
        return self.name
    
    def apply_results(self, character):
        self.results.apply(character)
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
                    #print("lastCompleted:", lastCompleted)

                    if self.frequency == 'DAY':
                        #print("we are here :D")
                        todayDate = int(today.strftime('%d'))
                        lastCompletedDate = int(lastCompleted.strftime('%d'))    
                        #print("lastCompletedDate:", lastCompletedDate)
                        if todayDate == lastCompletedDate:
                            #print("should only happen once")
                            return False
                        
                    elif self.frequency == 'WEEK':
                        dateDiff = today-lastCompleted
                        if dateDiff.days < 7:
                            if today.weekday() >= lastCompleted.weekday():
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
        if not self.is_active:
            return False
        elif character.level < self.levelMin or \
            character.level > self.levelMax:
            return False
        elif profile.is_premium and self.is_premium:
            return False
        
        # Quest passed the test
        return True

    
class QuestResults(models.Model):
    quest = models.OneToOneField('Quest', on_delete=models.CASCADE, related_name='results')
    dynamic_rewards = models.JSONField(default=dict, null=True, blank=True)
    xp_rate = models.IntegerField(default=1)
    coin_reward = models.IntegerField(default=0)
    buffs = models.JSONField(default=list, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Quest results for Quest '{self.quest.id}': {json.dumps(self.dynamic_rewards, indent=2)}"

    def calculate_xp_reward(self, character, duration):
        """Calculates XP reward based on quest duration and other factors"""
        character_level = character.level
        quest_completions = character.get_quest_completions(self.quest).first()
        base_xp = self.xp_rate
        time_xp = base_xp * duration
        level_scaling = 1 + (character_level * 0.05)
        repeat_penalty = 0.99 ** quest_completions.times_completed
        final_xp = time_xp * level_scaling * repeat_penalty
        return max(1, round(final_xp))

    @transaction.atomic
    def apply(self, character):
        """Apply rewards/results to a given character"""
        #character.add_coins(self.coin_reward)
        character.coins += self.coin_reward

        for key, value in self.dynamic_rewards.items():
            if hasattr(character, f"apply_{key}"):
                method = getattr(character, f"apply_{key}")
                method(value)
            elif hasattr(character, key):
                setattr(character, key, getattr(character, key) + value if isinstance(value, (int, float)) else value)

        #print("self.buffs:", self.buffs)
        for buff_name in self.buffs:
            #print("buff_name:", buff_name)
            buff = Buff.objects.get(name=buff_name)
            #print("questresults apply method, buff:", buff)
            applied_buff = AppliedBuff.objects.create(
                name=buff.name,
                duration= buff.duration,
                amount=buff.amount,
                buff_type=buff.buff_type,
                attribute=buff.attribute,
            )
            character.buffs.add(applied_buff)
        character.save()

class QuestRequirement(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name="quest_requirements")
    prerequisite = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name="required_for") 
    times_required = models.PositiveIntegerField(default=1)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.prerequisite.name} required {self.times_required} time(s) for {self.quest.name}"


class QuestCompletion(models.Model):
    character = models.ForeignKey('character.Character', on_delete=models.CASCADE) # don't add related_name, use character.quest_completions!
    quest = models.ForeignKey('gameplay.Quest', on_delete=models.CASCADE, related_name='quest_completions')
    times_completed = models.PositiveIntegerField(default=1)
    last_completed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('character', 'quest')
    
    def __str__(self):
        return f"character {self.character.name} has completed {self.quest.name}"


class Activity(models.Model):
    profile = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name="activities")
    name = models.CharField(max_length=255)
    duration = models.PositiveIntegerField(default=0)  # Time spent
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    xp_rate = models.IntegerField(default=1)
    skill = models.ForeignKey('Skill', on_delete=models.SET_NULL, null=True, blank=True, related_name="activities")
    project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, related_name="activities")
    
    class Meta:
        ordering = ['-created_at'] # Most recent activities first

    def update_name(self, new_name):
        self.name = new_name
        self.save(update_fields=['name'])

    def add_time(self, num):
        self.duration += num
        self.save(update_fields=['duration'])

    def new_time(self, num):
        self.duration = num
        self.save(update_fields=['duration'])

    def calculate_xp_reward(self):
        """
        Calculate XP reward for this activity, considering buffs.
        """
        base_xp = self.duration * self.xp_rate
        final_xp = self.profile.apply_buffs(base_xp, 'xp')
        return final_xp

    def __str__(self):
        return f"activity {self.name}, created {self.created_at}, duration {self.duration}, profile {self.profile.name}"
    

class Skill(models.Model):
    profile = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    time = models.PositiveIntegerField(default=0)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    total_activities = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Project(models.Model):
    profile = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=2000)
    time = models.PositiveIntegerField(default=0)
    total_activities = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Timer(models.Model):
    start_time = models.DateTimeField(null=True, blank=True)
    elapsed_time = models.IntegerField(default=0)  # Time in seconds
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('waiting', 'Waiting'),
        ('completed', 'Completed'),
        ('empty', 'Empty'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='empty')

    class Meta:
        abstract = True
            
    def get_elapsed_time(self):
        this_round = (now() - self.start_time).total_seconds() if self.start_time else 0
        return int(this_round + self.elapsed_time)
    
    def update_time(self):
        if self.start_time:
            self.elapsed_time = self.get_elapsed_time()
            self.save()

    def start(self):
        if self.status != 'active':
            self.status = 'active'
            self.start_time = now()
            self.save()
            
    def pause(self):
        if self.status != 'paused':
            self.status = 'paused'
            self.update_time()
            self.start_time = None
            self.save()

    def set_waiting(self):
        if self.status != 'waiting':
            self.status = 'waiting'
            self.save()

    def complete(self):
        if self.status != 'completed':
            self.update_time()
            self.status = 'completed'
            
    def reset(self):
        if self.status != 'empty':
            self.status = 'empty'
            self.elapsed_time = 0
            self.start_time = None

class ActivityTimer(Timer):
    profile = models.OneToOneField('users.profile', on_delete=models.CASCADE, related_name='activity_timer')
    activity = models.ForeignKey('Activity', on_delete=models.SET_NULL, related_name='activity_timer', null=True, blank=True)

    def __str__(self):
        return f"ActivityTimer for {self.profile.name}: status {self.status}"

    def new_activity(self, activity):
        self.reset()
        self.activity = activity
        self.set_waiting()
        self.save()

    def pause(self):
        #print("Activity timer pause()")
        super().pause()
        self.update_activity_time()

    def update_activity_time(self):
        if self.activity:
            self.activity.new_time(self.elapsed_time)
            self.save()
        else:
            logger.info(f"[ACTIVITYTIMER.UPDATE_ACTIVITY_TIME] No activity found for timer {self}")

    def complete(self):
        super().complete()
        xp = self.calculate_xp()
        self.reset()
        return xp

    def reset(self):
        super().reset()
        self.activity = None
        self.save()

    def calculate_xp(self):
        return self.activity.calculate_xp_reward()


class QuestTimer(Timer):
    character = models.OneToOneField('character.Character', on_delete=models.CASCADE, related_name='quest_timer')
    quest = models.ForeignKey('Quest', on_delete=models.SET_NULL, related_name='quest_timer', null=True, blank=True)
    duration = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        #print(f"QuestTimer saved. {self}")
        #traceback.print_stack()
        super().save(*args, **kwargs)

    def change_quest(self, quest, duration=5):
        self.reset()
        #print(QuestTimer.objects.filter(pk=self.pk).values())
        self.quest = quest
        self.duration = duration
        self.set_waiting()
        #print("QuestTimer after change_quest, just before save", self)
        self.save()
        #print(QuestTimer.objects.filter(pk=self.pk).values())

    def complete(self):
        super().complete()
        #logger.debug(f"[QUESTTIMER.COMPLETE] {self}")
        xp = self.calculate_xp()
        self.save()
        return xp

    def reset(self):
        super().reset()
        self.quest = None
        self.save()
        #print("Quest timer reset. Quest:", self.quest)

    def calculate_xp(self):
        return self.quest.results.calculate_xp_reward(self.character, self.duration)

    def get_remaining_time(self):
        if self.status == 'active':
            elapsed = self.get_elapsed_time()
            return max(self.duration - int(elapsed + self.elapsed_time), 0)
        return max(self.duration - self.elapsed_time, 0)

    def is_complete(self):
        return self.get_remaining_time() <= 0

    def __str__(self):
        return f"QuestTimer for {self.character.name}: status {self.status}" #quest {self.quest.name}, 
    





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
    last_updated = models.DateTimeField(auto_now=True)

class AppliedBuff(Buff):
    applied_at = models.DateTimeField(auto_now_add=True)
    # How do you include setup method as part of creation? Signal?

    def setup(self):
        end_time = now() + timedelta(seconds=self.duration)
        ends_at = models.DateTimeField(end_time)
        self.save()

    def is_active(self):
        """Check if buff is still active."""
        return now() < self.applied_at + timedelta(seconds=self.duration)
    
    def calc_value(self, total_value):
        if self.is_active():
            if self.buff_type == 'additive':
                total_value += self.amount
            elif self.buff_type == 'multiplicative':
                total_value *= self.amount
        return total_value

# Don't think I actually need this after all!
# I can use created_at fields which have time too
class DailyStats(models.Model):
    created_at = models.DateTimeField(auto_now_add=True) #auto_now_add=True
    newUsers = models.PositiveIntegerField(default=0)
    questsCompleted = models.PositiveIntegerField(default=0)
    activitiesCompleted = models.PositiveIntegerField(default=0)
    activityTimeLogged = models.PositiveIntegerField(default=0)
    today = now().date()
    recordDate = models.DateField(default=now)

    def __str__(self):
        return f"Daily Stats for {self.recordDate} \
            {self.newUsers} new users, "

class GameWorld(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    num_profiles = models.PositiveIntegerField(default=0)
    highest_login_streak_ever = models.PositiveIntegerField(default=0)
    highest_login_streak_current = models.PositiveIntegerField(default=0)
    total_activity_num = models.PositiveIntegerField(default=0)
    total_activity_time = models.PositiveIntegerField(default=0)
    #activities_num_average = models.Float?
    #activities_time_average = models.Float?

    def time_up(self):
        return now()-self.created_at

    def update(self):
        profiles = Profile.objects.all()
        self.num_profiles = len(profiles)
        for profile in profiles:
            if self.highest_login_streak_ever < profile.login_streak_max:
                self.highest_login_streak_ever = profile.login_streak_max
            if self.highest_login_streak_current < profile.login_streak:
                self.highest_login_streak_current = profile.login_streak

        activities = Activity.objects.all()
        self.total_activity_num = len(activities)
        total_activity_time = 0
        for activity in activities:
            total_activity_time += activity.duration
        self.total_activity_time = total_activity_time

        activities_num_average = self.total_activity_num / self.num_profiles
        activities_time_average = self.total_activity_time / self.num_profiles

        questsCompleted = QuestCompletion.objects.all()
        unique_quests = set()
        total_quests = 0
        for qc in questsCompleted:
            unique_quests.add(qc.quest)
            total_quests += qc.times_completed

    def createDailyStats(self):
        ds = DailyStats.objects.create(
            name=f"DailyStats for world {self.name}",
            
        )

    def __str__(self):
        return f"This game has been running for {self.time_up()} since {self.created_at}"
