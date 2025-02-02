from django.contrib import admin
from .models import CharacterRelationship, Partnership, CharacterRole, CharacterProgression

# Register your models here.

@admin.register(CharacterRelationship)
class CharacterRelationshipAdmin(admin.ModelAdmin):
    list_display = [
        'character1',
        'character2',
        'relationship_type',
    ]
    fields = [
        'character1',
        'character2',
        'relationship_type',
        'strength',
        'history',
        'biological',
    ]

@admin.register(Partnership)
class PartnershipAdmin(admin.ModelAdmin):
    list_display = [
        'partner1',
        'partner2',
    ]

    fields = [
        'partner1',
        'partner2',
        'total_births',
        'last_birth_date',
        'partner_is_pregnant',
    ]

@admin.register(CharacterRole)
class CharacterRoleAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'description',
    ]

@admin.register(CharacterProgression)
class CharacterProgressionAdmin(admin.ModelAdmin):
    list_display = [
        'character',
        'role',
    ]
    fields = [
        'character',
        'role',
        'experience',
        'date_started',
        'base_progression_rate',
        'player_acceleration_factor',
    ]