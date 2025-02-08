from django.db import models, transaction
from users.models import Person, Profile
from gameplay.models import Buff, AppliedBuff
from datetime import datetime
import json
import math
from random import random
from django.utils.timezone import now, timedelta


######################################################

#               CHARACTER APP

######################################################

# Create your models here.

class Character(Person):
    quest_completions = models.ManyToManyField('gameplay.Quest', through='gameplay.QuestCompletion', related_name='completed_by')
    total_quests = models.PositiveIntegerField(default=0)

    first_name = models.CharField(max_length=50, default="")
    last_name = models.CharField(max_length=50, default="", null=True, blank=True)
    backstory = models.TextField(default="")
    parents = models.ManyToManyField('self', related_name='children', symmetrical=False)
    gender = models.CharField(max_length=50, default="None")
    is_pregnant = models.BooleanField(default=False)
    pregnancy_start_date = models.DateField(null=True, blank=True)
    pregnancy_due_date = models.DateTimeField(null=True, blank=True)
    dob = models.DateField(default=now)
    dod = models.DateField(null=True, blank=True)
    cause_of_death = models.CharField(max_length=255, null=True, blank=True)
    coins = models.PositiveIntegerField(default=0)
    reputation = models.IntegerField(default=0)
    buffs = models.ManyToManyField('gameplay.Buff', related_name='characters', blank=True)
    is_npc = models.BooleanField(default=True)

    def __str__(self):
        return self.name if self.name else "Unnamed character"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_age(self):
        return now().date() - self.dob
    
    def die(self):
        self.dob = now().date()
        self.save()

    def is_alive(self):
        """Returns True if character is alive"""
        return self.dod is None
    
    def start_quest(self, quest):
        self.quest_timer.change_quest(quest)

    def is_player_controlled(self):
        return self.profile is not None

    def get_quest_completions(self, quest):
        return QuestCompletion.objects.filter(character=self, quest=quest)

    @transaction.atomic
    def complete_quest(self, quest):
        with transaction.atomic():
            completion, created = QuestCompletion.objects.get_or_create(
                character=self,
                quest=quest,
            )
            if not created:
                completion.times_completed += 1
            completion.save()
        if hasattr(quest, 'questreward'):
            quest_reward = quest.questreward
            print("quest reward:", quest_reward)
            quest_reward.apply(self)

        self.total_quests += 1
        self.save()

    def start_pregnancy(self):
        from gameworld.models import Partnership
        if not self.is_pregnant:
            self.is_pregnant = True
            self.pregnancy_start_date = now().date()
        else:
            print(f"{self.name} is already pregnant.")
            return
        
        partner = self.get_partner()
        if partner:
            partnership = Partnership.objects.get(
                models.Q(partner1=self, partner2=partner) | models.Q(partner1=partner, partner2=self)
            )
            if not partnership.partner_is_pregnant:
                partnership.partner_is_pregnant = True
                partnership.save()
                print(f"{self.name} and {partner.name} are now expecting")
        self.save()

    def handle_childbirth(self):
        from gameworld.models import Partnership
        child_name = f"Child of {self.first_name}"
        child = Character.objects.create(
            name=child_name,
            dob=now().date(),
            gender="Male" if random() < 50 else "Female",
            x_coordinate=self.x_coordinate,
            y_coordinate=self.y_coordinate,
        )

        child.parents.add(self)
        partner = self.get_partner()
        if partner:
            child.parents.add(partner)
            partnership = Partnership.objects.get(
                models.Q(partner1=self, partner2=partner) | models.Q(partner1=partner, partner2=self)
            )
            partnership.last_birth_date = now().date()
            partnership.total_births += 1
            partnership.partner_is_pregnant = False
            partnership.save()
        
    def handle_miscarriage(self):
        self.is_pregnant = False
        self.pregnancy_start_date = None
        self.save()

    def get_miscarriage_change(self):
        chance = 0.05
        if self.get_age() > 40 * 365:
            chance += 0.10
        return chance

    def get_partner(self):
        """Get the character's active partner if one exists"""
        from gameworld.models import Partnership
        partnerships = Partnership.objects.filter(
            models.Q(partner1=self) | models.Q(partner2=self),
        )
        if partnerships.exists():
            partnership = partnerships.first()
            return partnership.partner1 if partnership.partner2 == self else partnership.partner2
        return None
    
    def is_in_partnership(self):
        from gameworld.models import Partnership
        return Partnership.objects.filter(
            models.Q(partner1=self) | models.Q(partner2=self),
        ).exists()
    
    def add_partner(self, partner):
        from gameworld.models import Partnership
        if not self.is_in_partnership():
            partnership = Partnership.objects.create(partner1=self, partner2=partner)
            return partnership
        return None

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
