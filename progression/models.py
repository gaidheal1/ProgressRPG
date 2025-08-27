# progression/models.py
from django.db import models
from django.utils import timezone


class TimeRecord(models.Model):
    """
    Abstract base model for tracking time-based records, such as quests or activities.

    Stores metadata about start, completion, duration, and XP rewards.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(max_length=2000, blank=True)
    duration = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    xp_gained = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def rename(self, new_name: str):
        """
        Update the record's name.
        """
        self.name = new_name
        self.save(update_fields=["name"])
        return self

    def add_time(self, num: int):
        """
        Increase the record's duration by a given amount.
        """
        self.duration += num
        self.save(update_fields=["duration"])
        return self

    def new_time(self, num: int):
        """
        Set the record's duration to a new value.
        """
        self.duration = num
        self.save(update_fields=["duration"])
        return self

    def start(self):
        """
        Mark the record as started if not already started.

        Returns the timestamp when started.
        """
        if self.started_at:
            return
        self.started_at = timezone.now()
        self.save(update_fields=["started_at"])
        return self.started_at

    def complete(self):
        """
        Mark the record as completed if not already complete.

        Returns the completion timestamp.
        """
        if self.is_complete:
            return
        self.completed_at = timezone.now()
        self.is_complete = True
        self.save(update_fields=["completed_at", "is_complete"])
        return self.completed_at

    def is_completed(self):
        """
        Return True if the record has been completed.
        """
        return self.is_complete

    def calculate_xp_reward(self):
        """
        Calculate and store the XP reward based on duration.

        Currently, XP gained equals total duration.
        """
        xp = self.duration
        self.xp_gained = xp
        self.save(update_fields=["xp_gained"])
        return self

    class Meta:
        abstract = True


class Activity(TimeRecord):
    """
    Represents an activity tracked by a user.

    Inherits common time tracking fields and behaviour from ``TimeRecord``.
    Activities may be linked to a skill or project, and can be private.
    """

    profile = models.ForeignKey(
        "users.Profile", on_delete=models.CASCADE, related_name="activities"
    )
    is_private = models.BooleanField(default=False)
    skill = models.ForeignKey(
        "gameplay.Skill",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
    )
    project = models.ForeignKey(
        "gameplay.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
    )

    class Meta:
        ordering = ["-created_at"]
        db_table = "progression_activity"

    def __str__(self):
        """
        Return a readable name for the activity, masking private ones.
        """
        return "Private activity" if self.is_private else f"activity {self.name}"


class CharacterQuest(TimeRecord):
    """
    Represents a quest assigned to a character.

    Inherits common time tracking fields and behaviour from ``TimeRecord``.
    Includes extra narrative fields (intro/outro text), user-selected
    duration, and stage progression data.
    """

    character = models.ForeignKey(
        "character.Character", on_delete=models.CASCADE, related_name="character_quests"
    )
    intro_text = models.TextField(max_length=2000, blank=True)
    outro_text = models.TextField(max_length=2000, blank=True)
    quest_duration = models.PositiveIntegerField(default=0)
    stages = models.JSONField(default=list)
    stagesFixed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"character_quest {self.name}"
