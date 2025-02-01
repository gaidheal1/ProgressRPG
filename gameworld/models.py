# gameworld.models

from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey("gameplay.Character", on_delete=models.SET_NULL, null=True, blank=True, related_name='owner')
    public = models.BooleanField(default=True)
    upkeep = models.PositiveIntegerField(default=0)
    ROLE_CHOICES = [
        ("domestic", "Domestic"),
        ("commercial", "Commercial"),
        ("guild", "Guild"),
        ("religious", "Religious"),
        ("military", "Military"),
        ("none", "None"),
    ]
    role = models.CharField(max_length=50, default="none")
    x_coordinate = models.IntegerField()  # X coordinate (horizontal position)
    y_coordinate = models.IntegerField()  # Y coordinate (vertical position)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CharacterRelationship(models.Model):
    character1 = models.ForeignKey(
        'gameplay.Character', on_delete=models.CASCADE, related_name='relationship_as_char1'
    )
    character2 = models.ForeignKey(
        'gameplay.Character', on_delete=models.CASCADE, related_name='relationship_as_char2'
    )
    
    RELATIONSHIP_TYPES = [
        ('friend', 'Friend'),
        ('rival', 'Rival'),
        ('mentor', 'Mentor'),
        ('enemy', 'Enemy'),
        ('ally', 'Ally'),
        ('romantic', 'Romantic'),
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
