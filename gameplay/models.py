"""
Models for the gameplay application, including quests, requirements, completions,
activities, timers, and server messages. These models are used to manage in-game
logic, track player progress, and handle rewards and buffs.

Author: Duncan Appleby
"""

# gameplay.models

#from django_stubs_ext.db.models import Related
from django.db import models, transaction
#from django.db.models import ForeignKey
from django.db.models import QuerySet
from django.utils.timezone import now, timedelta
from typing import Optional, Iterable, Dict, Any, cast, List, TYPE_CHECKING
import json, logging

if TYPE_CHECKING:
    from character.models import Character

logger = logging.getLogger("django")



class Quest(models.Model):
    """
    Represents a quest in the game, with eligibility criteria, duration, and category.

    Attributes:
        name (str): The name of the quest.
        description (str): A detailed description of the quest.
        intro_text (str): The text shown when starting the quest.
        outro_text (str): The text shown when completing the quest.
        DURATION_CHOICES (list): Fixed durations available for the quest.
        duration_choices (list): Customizable durations for the quest, in seconds.
        created_at (datetime): The timestamp when the quest was created.
        start_date (datetime): The start date of the quest.
        end_date (datetime): The end date of the quest.
        is_active (bool): Indicates whether the quest is currently active.
        stages (list): A list of quest stages.
        category (str): The category of the quest (e.g., trade, event).
        is_premium (bool): Indicates whether the quest is available only for premium users.
        levelMin (int): Minimum level required to attempt the quest.
        levelMax (int): Maximum level allowed for the quest.
        canRepeat (bool): Indicates whether the quest can be repeated after completion.
        frequency (str): How often the quest can be attempted (e.g., daily, weekly).
    """
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=2000, blank = True)
    intro_text = models.TextField(max_length=2000, blank = True)
    outro_text = models.TextField(max_length=2000, blank = True)
    #DURATION_CHOICES = [(300 * i) for i in range(1, 7)]

    @staticmethod
    def default_duration_choices() -> List[int]:
        return [(300 * i) for i in range(1, 7)]
    
    duration_choices: Any = models.JSONField(default=default_duration_choices)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    stages: Any = models.JSONField(default=list)

    class Category(models.TextChoices):
        NONE = 'NONE', 'No category'
        TRADE = 'TRADE', 'Trade'
        RECUR = 'RECUR', 'Recurring'
        EVENT = 'EVENT', 'Event'

    category = models.CharField(max_length=20, default=Category.NONE)
    results: Optional["QuestResults"] = None

    # Eligibility criteria
    is_premium = models.BooleanField(default=True)
    levelMin = models.IntegerField(default=0)
    levelMax = models.IntegerField(default=0)
    canRepeat = models.BooleanField(default=False)
    quest_requirements: QuerySet["QuestRequirement"]
    quest_completions: QuerySet["QuestCompletion"]

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
    
    def list_requirements(self) -> Iterable["QuestRequirement"]:
        return self.quest_requirements.all()
        
    def apply_results(self, character: "Character"):
        """
        Apply the results and rewards of the quest to the specified character.

        :param character: The character to whom the quest rewards will be applied.
        :type character: Character
        """
        if self.results:
            self.results.apply(character)
            character.save()  # Ensure all changes are persisted

    def requirements_met(self, completed_quests):
        """
        Checks if the character meets all prerequisites for the quest.

        :param completed_quests: A dictionary mapping quest IDs to completion counts.
        :type comppleted_quests: dict
        :return: True if all requirements are met, False otherwise.
        :rtype: bool
        """
        #print("you have arrived in requirements_met")
        if hasattr(self, 'quest_requirements'):
            for requirement in self.list_requirements():
                completed_count = completed_quests.get(requirement.prerequisite, 0)
                if completed_count < requirement.times_required:
                    return False
            return True
    
    def not_repeating(self, character: "Character"):
        """
        Verify whether the quest can be repeated for the given character.

        :param character: The character attempting the quest.
        :type character: Character
        :return: True if the quest can be repeated, False otherwise.
        :rtype: bool
        """
        #print("you have arrived in not_repeating")
        if hasattr(self, 'quest_completions'):
            completions = self.quest_completions.all()
            # Check repeating
            if self.canRepeat == False:
                for completion in completions:
                    if completion.character == character:
                        if completion.times_completed >= 1:
                            return False
            return True

    def frequency_eligible(self, character: "Character"):
        """
        Check if the quest is eligible to be undertaken based on its frequency.

        :param character: The character attempting the quest.
        :type character: Character
        :return: True if the quest is frequency-eligible, False otherwise.
        :rtype: bool
        """
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
    
    def checkEligible(self, character: "Character", profile):
        """
        Determine if the quest is eligible for the given character and profile.

        :param character: The character attempting the quest.
        :type character: Character
        :param profile: The profile associated with the character.
        :type profile: Profile
        :return: True if the quest is eligible, False otherwise.
        :rtype: bool
        """
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
    """
    Stores the results and rewards for a quest, including experience points,
    coins, and buffs.

    Attributes:
        quest (Quest): The quest associated with these results.
        dynamic_rewards (dict): Additional rewards in JSON format.
        xp_rate (int): The rate of experience points awarded.
        coin_reward (int): The number of coins awarded.
        buffs (list): A list of buffs granted upon completion.
        last_updated (datetime): The timestamp of the last update.
    """
    quest = models.OneToOneField('Quest', on_delete=models.CASCADE, related_name='results')
    dynamic_rewards = models.JSONField(default=dict, null=True, blank=True)
    xp_rate = models.IntegerField(default=1)
    coin_reward = models.IntegerField(default=0)
    buffs = models.JSONField(default=list, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Quest results for Quest '{self.quest.id}': {json.dumps(self.dynamic_rewards, indent=2)}"

    def calculate_xp_reward(self, character: "Character", duration: int):
        """
        Calculates the experience points awarded based on quest duration.

        :param character: The character completing the quest.
        :type character: Character
        :param duration: Time spent on the quest.
        :type duration: int

        :return: The calculated experience points.
        :rtype: int
        """
        character_level = character.level
        quest_completions = character.get_quest_completions(self.quest).first()
        base_xp = self.xp_rate
        time_xp = base_xp * duration
        level_scaling = 1 + (character_level * 0.05)
        repeat_penalty = 0.99 ** quest_completions.times_completed
        final_xp = time_xp * level_scaling * repeat_penalty
        return max(1, round(final_xp))

    @transaction.atomic
    def apply(self, character: "Character"):
        """
        Apply the rewards associated with this quest to the given character, including
        coins, dynamic rewards, and buffs.

        :param character: The character receiving the rewards.
        :type character: Character
        """
        logger.info(f"[QUESTRESULTS.APPLY] Applying results for quest {self.quest.name} to character {character.name}")
        #character.add_coins(self.coin_reward)
        character.coins += self.coin_reward

        if self.dynamic_rewards:
            rewards = cast(Dict[str, Any], self.dynamic_rewards or {})
            for key, value in rewards.items():
                if hasattr(character, f"apply_{key}"):
                    method = getattr(character, f"apply_{key}")
                    method(value)
                elif hasattr(character, key):
                    current_value = getattr(character, key)
                    if isinstance(current_value, (int, float)):
                        setattr(character, key, current_value + value)
                    else:
                        setattr(character, key, value)
        else:
            logger.info(f"[QUESTRESULTS.APPLY] No dynamic rewards found for quest {self.quest.name}.")

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
    """
    Represents the prerequisite quests a quest needs, including required completions.

    Attributes:
        quest (Quest): The quest with the requirement.
        prerequisite (Quest): The quest that must be completed first.
        times_required (int): The number of times the prerequisite quest must be completed.
        last_updated (datetime): The timestamp of the last update.
    """
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name="quest_requirements")
    prerequisite = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name="required_for") 
    times_required = models.PositiveIntegerField(default=1)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('quest', 'prerequisite')

    def __str__(self):
        return f"{self.prerequisite.name} required {self.times_required} time(s) for {self.quest.name}"


class QuestCompletion(models.Model):
    """
    Tracks the completion details for a quest, including the number of times
    completed and the last completion timestamp.

    Attributes:
        character (Character): The character who completed the quest.
        quest (Quest): The quest being tracked.
        times_completed (int): The number of times the quest has been completed.
        last_completed (datetime): The timestamp of the last completion.
    """
    character = models.ForeignKey('character.Character', on_delete=models.CASCADE) # don't add related_name, use character.quest_completions!
    quest = models.ForeignKey('gameplay.Quest', on_delete=models.CASCADE, related_name='quest_completions')
    times_completed = models.PositiveIntegerField(default=1)
    last_completed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('character', 'quest')
    
    def __str__(self):
        return f"character {self.character.name} has completed {self.quest.name}"


class Activity(models.Model):
    """
    Represents an activity undertaken by a profile, with tracking for time spent,
    experience gained, and associated projects or skills.

    Attributes:
        profile (Profile): The user profile associated with the activity.
        name (str): The name of the activity.
        duration (int): The duration of the activity in seconds.
        created_at (datetime): The timestamp when the activity was created.
        last_updated (datetime): The timestamp of the last update.
        xp_rate (int): The rate of experience points earned per second.
        skill (Skill): The skill associated with the activity.
        project (Project): The project associated with the activity.
    """
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

    def update_name(self, new_name: str):
        """
        Update the name of the activity.

        :param new_name: The new name to set for the activity.
        :type new_name: str
        """
        self.name = new_name
        self.save(update_fields=['name'])

    def add_time(self, num: int):
        """
        Add additional time to the activity's duration.

        :param num: The amount of time to add, in seconds.
        :type num: int
        """
        self.duration += num
        self.save(update_fields=['duration'])

    def new_time(self, num):
        """
        Set a new total duration for the activity.

        :param num: The new total time for the activity, in seconds.
        :type num: int
        """
        self.duration = num
        self.save(update_fields=['duration'])

    def calculate_xp_reward(self) -> int:
        """
        Calculate the experience points (XP) reward for the activity.

        :return: The calculated XP reward, adjusted by any active buffs.
        :rtype: int
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
    """
    An abstract base model that represents a general timer for activities
    such as quests or projects.

    Attributes:
        start_time (datetime): The time the timer was started.
        elapsed_time (int): The total elapsed time for the timer, in seconds.
        created_at (datetime): The timestamp when the timer was created.
        last_updated (datetime): The timestamp of the last timer update.
        status (str): The current status of the timer (e.g., active, paused).
    """
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
        """
        Calculate the total elapsed time for the timer.

        :return: The elapsed time in seconds.
        :rtype: int
        """
        this_round = (now() - self.start_time).total_seconds() if self.start_time else 0
        return int(this_round + self.elapsed_time)
    
    def update_time(self):
        """
        Update the elapsed time for the timer based on the current time.
        """
        if self.start_time:
            self.elapsed_time = self.get_elapsed_time()
            self.save()

    def start(self):
        """
        Start the timer and set its status to 'active'.
        """
        if self.status != 'active':
            self.status = 'active'
            self.start_time = now()
            self.save()
    
    def is_active(self):
        """
        Check if the timer is currently active.

        :return: True if the timer is active, False otherwise.
        :rtype: bool
        """
        return self.status == 'active'
    
    def pause(self):
        """
        Pause the timer and update its elapsed time.
        """
        if self.status not in ['paused',]:
            self.status = 'paused'
            self.update_time()
            self.start_time = None
            self.save()

    def set_waiting(self):
        """
        Set the timer status to 'waiting'.
        """
        if self.status != 'waiting':
            self.status = 'waiting'
            self.save()

    def complete(self) -> int:
        """
        Mark the timer as 'completed' and update its elapsed time.
        """
        if self.status != 'completed':
            self.update_time()
            self.status = 'completed'
        return 0
            
    def reset(self):
        """
        Reset the timer, clearing all elapsed time and setting status to 'empty'.
        """
        if self.status != 'empty':
            self.status = 'empty'
            self.elapsed_time = 0
            self.start_time = None






class ActivityTimer(Timer):
    """
    A timer that tracks progress on player activities.

    Attributes:
        profile (Profile): The user profile associated with the timer.
        activity (Activity): The activity being tracked.
    """
    profile = models.OneToOneField('users.profile', on_delete=models.CASCADE, related_name='activity_timer')
    activity = models.ForeignKey('Activity', on_delete=models.SET_NULL, related_name='activity_timer', null=True, blank=True)

    def __str__(self):
        return f"ActivityTimer for {self.profile.name}: status {self.status}"

    def new_activity(self, activity: Activity):
        """
        Assign a new activity to the timer.

        :param activity: The activity to associate with the timer.
        :type activity: Activity
        """
        self.reset()
        self.activity = activity
        self.set_waiting()
        self.save()

    def pause(self):
        """
        Pause the activity timer and update the associated activity's duration.
        """
        #print("Activity timer pause()")
        super().pause()
        self.update_activity_time()

    def update_activity_time(self):
        """
        Update the total duration of the associated activity.
        """
        if self.activity:
            self.activity.new_time(self.elapsed_time)
            self.save()
        else:
            logger.info(f"[ACTIVITYTIMER.UPDATE_ACTIVITY_TIME] No activity found for timer {self}. Resetting timer.")
            self.reset()

    def complete(self):
        """
        Complete the activity timer and calculate the XP reward for the activity.

        :return: The XP reward for the activity.
        :rtype: int
        """
        super().complete()
        xp = self.calculate_xp()
        self.reset()
        return xp

    def reset(self):
        """
        Reset the activity timer and dissociate the current activity.
        """
        super().reset()
        self.activity = None
        self.save()

    def calculate_xp(self):
        """
        Calculate the XP reward for the associated activity.

        :return: The calculated XP reward.
        :rtype: int
        """
        return self.activity.calculate_xp_reward()






class QuestTimer(Timer):
    """
    A timer that tracks progress on quests for a character.

    Attributes:
        character (Character): The character associated with the timer.
        quest (Quest): The quest being tracked by the timer.
        duration (int): The total duration of the timer in seconds.
    """
    character = models.OneToOneField('character.Character', on_delete=models.CASCADE, related_name='quest_timer')
    quest = models.ForeignKey('Quest', on_delete=models.SET_NULL, related_name='quest_timer', null=True, blank=True)
    duration = models.IntegerField(default=0)

    # def save(self, *args, **kwargs):
    #     #print(f"QuestTimer saved. {self}")
    #     #traceback.print_stack()
    #     super().save(*args, **kwargs)

    def change_quest(self, quest: Quest, duration: int):
        """
        Reset the timer and change the associated quest.

        :param quest: The new quest to associate with the timer.
        :type quest: Quest
        :param duration: The new duration for the quest, in seconds.
        :type duration: int
        """
        self.reset()
        self.quest = quest
        self.duration = duration
        self.set_waiting()
        self.save()

    def complete(self):
        """
        Mark the quest timer as complete and calculate XP for the quest.

        :return: The calculated XP reward.
        :rtype: int
        """
        super().complete()
        #logger.debug(f"[QUESTTIMER.COMPLETE] {self}")
        xp = self.calculate_xp()
        self.save()
        return xp

    def reset(self):
        """
        Reset the quest timer and dissociate the quest.
        """
        super().reset()
        self.quest = None
        self.save()
        #print("Quest timer reset. Quest:", self.quest)

    def calculate_xp(self):
        """
        Calculate the XP reward for the associated quest.

        :return: The calculated XP reward.
        :rtype: int
        """
        return self.quest.results.calculate_xp_reward(self.character, self.duration)

    def get_remaining_time(self):
        """
        Calculate the remaining time for the quest timer.

        :return: The remaining time in seconds.
        :rtype: int
        """
        if self.status == 'active':
            elapsed = self.get_elapsed_time()
            return max(self.duration - int(elapsed + self.elapsed_time), 0)
        return max(self.duration - self.elapsed_time, 0)

    def time_finished(self):
        """
        Check whether the quest timer is complete.

        :return: True if the timer has completed, False otherwise.
        :rtype: bool
        """
        #logger.debug(f"[QUESTTIMER.TIME FINISHED] Duration: {self.duration}, Remaining time: {self.get_remaining_time()}")
        return self.get_remaining_time() <= 0

    def __str__(self):
        return f"QuestTimer for {self.character.name}"
    

class ServerMessage(models.Model):
    """
    Represents a message sent by the server to a specific user profile. This
    can be used for notifications, responses, or event-driven communication.

    Attributes:
        profile (Profile): The user profile receiving the message.
        type (str): The type of message (e.g., event, action, error).
        action (str): The action associated with the message (e.g., 'quest_complete').
        data (dict): Event-specific data, stored as JSON.
        message (str): Optional textual content of the message.
        is_delivered (bool): Whether the message has been delivered to the user.
        created_at (datetime): The timestamp for when the message was queued.
    """
    profile = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='pending_notifications')
    type = models.CharField(
        max_length=20, choices=[
            ('event', 'Event'),
            ('server_message', 'Server Message'),
            ('action', 'Action'),
            ('response', 'Response'),
            ('error', 'Error'),
            ('notification', 'Notification'),
        ]
    )
    action = models.CharField(max_length=50)  # e.g., 'quest_complete', 'reward', 'message'
    data = models.JSONField()  # Store event-specific data as JSON
    message = models.TextField(max_length=2000, blank=True, null=True)
    is_delivered = models.BooleanField(default=False)  # Track delivery status
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when it was queued

    def to_dict(self):
        """
        Convert the server message to a dictionary representation.

        :return: A dictionary containing the message's type, action, data, and other metadata.
        :rtype: dict
        """
        message = {
            "type": self.type,
            "data": self.data,
            "action": self.action,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
        }
        return message
    
    def to_json(self):
        """
        Convert the server message to a JSON string for sending over WebSocket.

        :return: A JSON string representation of the server message.
        :rtype: str
        """
        return json.dumps(self.to_dict())
    
    def mark_delivered(self):
        """
        Mark the server message as delivered and update its status in the database.
        """
        self.is_delivered = True
        self.save(update_fields=['is_delivered'])

    def __str__(self):
        return f"{self.type.upper()} - {self.action} ({'Delivered' if self.is_delivered else 'Pending'})"
    
    @classmethod
    def get_unread(cls, profile):
        """
        Fetch all undelivered server messages for a specific profile.

        :param profile: The user profile to fetch unread messages for.
        :type profile: Profile
        :return: A QuerySet of undelivered server messages.
        :rtype: QuerySet
        """
        return cls.objects.filter(profile=profile, is_delivered=False)
    
    @classmethod
    def clear_old(cls, days=30):
        """
        Delete server messages that are older than the specified number of days.

        :param days: The age threshold (in days) for deleting old messages.
        :type days: int
        """
        cutoff_date = now() - timedelta(days=days)
        cls.objects.filter(created_at__lt=cutoff_date).delete()


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
    ends_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.ends_at:
            self.ends_at = now() + timedelta(seconds=self.duration)
        super().save(*args, **kwargs)

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


