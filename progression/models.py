# progression/models.py
from django.db import models
from django.utils import timezone


class timeRecord(models.Model):
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
        self.name = new_name
        self.save(update_fields=["name"])
        return self

    def add_time(self, num: int):
        self.duration += num
        self.save(update_fields=["duration"])
        return self

    def new_time(self, num: int):
        self.duration = num
        self.save(update_fields=["duration"])
        return self

    def start(self):
        if self.started_at:
            return
        self.started_at = timezone.now()
        self.save(update_fields=["started_at"])
        return self.started_at

    def complete(self):
        if self.is_complete:
            return
        self.completed_at = timezone.now()
        self.is_complete = True
        self.save(update_fields=["completed_at", "is_complete"])
        return self.completed_at

    def is_completed(self):
        return self.is_complete

    def calculate_xp_reward(self):
        xp = self.duration
        self.xp_gained = xp
        self.save(update_fields=["xp_gained"])
        return self

    class Meta:
        abstract = True

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "duration": self.duration,
            "started_at": self.started_at,
            "is_complete": self.is_complete,
            "completed_at": self.completed_at,
            "xp_gained": self.xp_gained,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
        }


class Activity(timeRecord):
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
        return "Private activity" if self.is_private else f"activity {self.name}"


class CharacterQuest(timeRecord):
    character = models.ForeignKey(
        "character.Character", on_delete=models.CASCADE, related_name="character_quests"
    )
    intro_text = models.TextField(max_length=2000, blank=True)
    outro_text = models.TextField(max_length=2000, blank=True)
    selected_duration = models.PositiveIntegerField(default=0)
    stages = models.JSONField(default=list)
    stagesFixed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"quest {self.name}"
