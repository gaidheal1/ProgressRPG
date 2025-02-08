# gameworld.models

from django.db import models
from django.utils import timezone


class CharacterRelationship(models.Model):
    character1 = models.ForeignKey(
        'character.Character', on_delete=models.CASCADE, related_name='relationship_as_char1'
    )
    character2 = models.ForeignKey(
        'character.Character', on_delete=models.CASCADE, related_name='relationship_as_char2'
    )
    
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
        ('cousin', 'Cousin'),
    ]
    
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES)
    strength = models.IntegerField(default=0)  # -100 (hatred) to 100 (deep bond)
    history = models.JSONField(default=dict, blank=True)  # Logs key events
    biological = models.BooleanField(default=True)  # True = blood relative, False = adopted/found family
    
    class Meta:
        unique_together = ('character1', 'character2', 'relationship_type')  # Prevent duplicates

    def adjust_strength(self, amount):
        """Modify relationship strength."""
        self.strength = max(min(self.strength + amount, 100), -100)
        self.save()

    def log_event(self, event):
        """Add an event to the history log."""
        self.history.setdefault('events', []).append(event)
        self.save()

    def __str__(self):
        bio = " (Biological)" if self.biological else " (Adopted)"
        return f"{self.character1.name} - {self.type} - {self.character2.name} ({self.strength}){bio}"

class Partnership(models.Model):
    partner1 = models.ForeignKey('character.Character', related_name='partner1_relationships', on_delete=models.CASCADE)
    partner2 = models.ForeignKey('character.Character', related_name='partner2_relationships', on_delete=models.CASCADE)

    last_birth_date = models.DateField(null=True, blank=True)
    total_births = models.PositiveIntegerField(default=0)

    partner_is_pregnant = models.BooleanField(default=False)

    def __str__(self):
        return f"Partnership between {self.partner1} and {self.partner2}"
    

class CharacterRole(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Char role: {self.name}"
    
    
class CharacterProgression(models.Model):
    character = models.OneToOneField('character.Character', on_delete=models.CASCADE)
    role = models.ForeignKey(CharacterRole, on_delete=models.CASCADE)
    experience = models.IntegerField(default=0)

    base_progression_rate = models.PositiveIntegerField(default=1)
    player_acceleration_factor = models.PositiveIntegerField(default=2)
    date_started = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"{self.character.name} - {self.role.name}"
    
    def update_progression(self):
        time_elapsed = (timezone.now().date() - self.date_started).days
        new_experience = time_elapsed * self.base_progression_rate
        self.experience += new_experience
        
        if not self.character.is_npc:
            self.experience *= self.player_acceleration_factor

        self.save()
    
