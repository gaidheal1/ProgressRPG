from django.db import models, transaction
from users.models import Person, Profile
from gameplay.models import Buff, AppliedBuff, QuestCompletion
from datetime import datetime
import json
import math
from random import random
from django.utils.timezone import now, timedelta

class CharacterRelationship(models.Model):
    characters = models.ManyToManyField('Character', through='CharacterRelationshipMembership')
    
    RELATIONSHIP_TYPES = [
        ('friend', 'Friend'),
        ('rival', 'Rival'),
        ('mentor', 'Mentor'),
        ('enemy', 'Enemy'),
        ('ally', 'Ally'),
        ('romantic', 'Romantic'),
        ('spouse', 'Spouse'),
        ('parent', 'Parent'),
        ('child', 'Child'),
        ('sibling', 'Sibling'),
    ]
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES)
    is_exclusive = models.BooleanField(default=False)
    strength = models.IntegerField(default=0)  # -100 (hatred) to 100 (deep bond)
    history = models.JSONField(default=dict, blank=True)  # Logs key events
    biological = models.BooleanField(default=True)  # True = blood relative, False = adopted/found family
    created_at = models.DateTimeField(default=now)
    last_updated = models.DateTimeField(default=now)
    romantic_relationship = models.OneToOneField('RomanticRelationship', on_delete=models.SET_NULL, null=True, blank=True)

    def get_members(self):
        return [char for char in self.characters.all()]
    
    def is_romantic(self):
        return self.relationship_type == 'romantic'

    def adjust_strength(self, amount):
        """Modify relationship strength."""
        self.strength = max(min(self.strength + amount, 100), -100)
        self.save()

    def log_event(self, event):
        """Add an event to the history log."""
        self.history.setdefault('events', []).append(event)
        self.save()

    def __str__(self):
        characters_list = [str(char) for char in self.get_members()]
        return f"{self.relationship_type} between {', '.join(characters_list)}"

class RomanticRelationship(models.Model):
    last_childbirth_date = models.DateField(null=True, blank=True)
    total_births = models.PositiveIntegerField(default=0)
    partner_is_pregnant = models.BooleanField(default=False)

    def __str__(self):
        return f"Partnership between {self.partner1} and {self.partner2}"


class CharacterRelationshipMembership(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE, related_name="characterrelationshipmembership")
    relationship = models.ForeignKey('CharacterRelationship', on_delete=models.CASCADE)
    role = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ('character', 'relationship')


class LifeCycleMixin(models.Model):
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    cause_of_death = models.CharField(max_length=255, null=True, blank=True)
    fertility = models.IntegerField(default=50)
    last_childbirth_date = models.DateField(null=True, blank=True)
    is_pregnant = models.BooleanField(default=False)
    pregnancy_start_date = models.DateField(null=True, blank=True)
    pregnancy_due_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def get_age(self):
        return now().date() - self.birth_date
    
    def die(self):
        self.death_date = now().date()
        self.save()

    def is_alive(self):
        return self.death_date is None

    def get_romantic_partners(self):
        return Character.objects.filter(
            characterrelationshipmembership__character=self,
            characterrelationshipmembership__relationship__relationship_type='romantic'
        )
    
    def is_fertile(self):
        return self.fertility > 0
    
    def can_reproduce_with(self, partner):
        if self.fertility <= 0 or partner.fertility <= 0:
            return False
        if self.sex == 'Male' and partner.sex == 'Male' or self.sex == 'Female' and partner.sex == 'Female':
            return False
        return True

    def attempt_pregnancy(self):
        romantic_partners = self.get_romantic_partners()

        for partner in romantic_partners:
            if self.can_reproduce_with(partner):
                if self.is_fertile() and not self.is_pregnant:
                    self.start_pregnancy(partner)
                    return True
        return False
    
    def start_pregnancy(self, partner):
        self.is_pregnant = True
        self.pregnancy_start_date = now().date()
        self.pregnancy_partner = partner
        
        self.save()

    def handle_childbirth(self):
        child_name = f"Child of {self.first_name}"
        child = Character.objects.create(
            name=child_name,
            birth_date=now().date(),
            sex="Male" if random() < 50 else "Female",
            x_coordinate=self.x_coordinate,
            y_coordinate=self.y_coordinate,
        )

        child.parents.add(self)
        if self.pregnancy_partner:
            child.parents.add(self.pregnancy_partner)
        child.save()
        
    def handle_miscarriage(self):
        self.is_pregnant = False
        self.pregnancy_start_date = None
        self.save()

    def get_miscarriage_change(self):
        chance = 0.05
        if self.get_age() > 40 * 365:
            chance += 0.10
        return chance


class Character(Person, LifeCycleMixin):
    quest_completions = models.ManyToManyField('gameplay.Quest', through='gameplay.QuestCompletion', related_name='completed_by')
    total_quests = models.PositiveIntegerField(default=0)

    first_name = models.CharField(max_length=50, default="")
    last_name = models.CharField(max_length=50, default="", null=True, blank=True)
    backstory = models.TextField(default="")
    parents = models.ManyToManyField('self', related_name='children', symmetrical=False, blank=True)
    sex = models.CharField(max_length=20, null=True)
    coins = models.PositiveIntegerField(default=0)
    reputation = models.IntegerField(default=0)
    buffs = models.ManyToManyField('gameplay.Buff', related_name='characters', blank=True)
    is_npc = models.BooleanField(default=True)
    position = models.OneToOneField('locations.Position', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def start_quest(self, quest):
        self.quest_timer.change_quest(quest)

    def get_quest_completions(self, quest):
        return QuestCompletion.objects.filter(character=self, quest=quest)

    @transaction.atomic
    def complete_quest(self):
        quest = self.quest_timer.quest
        print(f"Completing quest: {quest} for character {self}")
        if quest is None:
            print("Quest is None in Character.complete_quest!")
        with transaction.atomic():
            completion, created = QuestCompletion.objects.get_or_create(
                character=self,
                quest=quest,
            )
            if not created:
                completion.times_completed += 1
            completion.save()
        if hasattr(quest, 'results'):
            results = quest.results
            print("quest reward:", results)
            results.apply(self)

        xp_reward = self.quest_timer.complete()
        self.add_xp(xp_reward)
        self.total_quests += 1
        self.save()


class PlayerCharacterLink(models.Model):
    profile = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='character_link')
    character = models.ForeignKey('Character', on_delete=models.CASCADE, related_name='profile_link')
    date_linked = models.DateField(auto_now_add=True)
    date_unlinked = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def get_character(self, profile):
        link = PlayerCharacterLink.objects.filter(profile=profile, is_active=True).first()
        return link.character if link else None
    
    def unlink(self):
        """Marks link as inactive and records unlink date"""
        self.date_unlinked = now().date()
        self.is_active = False
        self.save()




class CharacterRole(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

class CharacterRoleSkill(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    related_role = models.ForeignKey('CharacterRole', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"


class CharacterProgression(models.Model):
    character = models.OneToOneField('character.Character', on_delete=models.CASCADE)
    role = models.ForeignKey(CharacterRole, on_delete=models.CASCADE)
    experience = models.IntegerField(default=0)

    base_progression_rate = models.PositiveIntegerField(default=1)
    player_acceleration_factor = models.PositiveIntegerField(default=2)
    date_started = models.DateField(default=now)
    
    def __str__(self):
        return f"{self.character.name} - {self.role.name}"
    
    def update_progression(self):
        time_elapsed = (now().date() - self.date_started).days
        new_experience = time_elapsed * self.base_progression_rate
        self.experience += new_experience
        
        if not self.character.is_npc:
            self.experience *= self.player_acceleration_factor

        self.save()
    