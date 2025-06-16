from django.contrib import admin
from .models import Character, PlayerCharacterLink, CharacterRelationship, CharacterRole, CharacterProgression
# Register your models here.


class LinkInline(admin.TabularInline):
    model = PlayerCharacterLink


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    # def current_player(self, obj):
    #     link = PlayerCharacterLink.objects.filter(character=obj, is_active=True).first()
    #     return link.profile.name if link else 'No player linked'
    
    # current_player.short_description = 'Current Player'

    fields = [
        'first_name', 
        'last_name',
        #'current_player',
        'is_npc',
        'backstory',
        'parents',
        'sex', 
        ('is_pregnant',
        'pregnancy_start_date',
        'pregnancy_due_date'),
        ('birth_date',
        'death_date'),
        'cause_of_death',
        'coins',
        'reputation',
        'total_quests',
    ]
    list_display = [
        'first_name',
        'last_name',
        'backstory',
        #'current_player',
        'is_npc',
        'birth_date',
        ]
    #list_editable = ['birth_date']
    search_fields = [
        'first_name',
        'last_name',
    ]
    inlines = [LinkInline]

#admin.site.register(Character, CharacterAdmin)

@admin.register(PlayerCharacterLink)
class PlayerCharacterLinkAdmin(admin.ModelAdmin):
    list_display = ['profile', 'character', 'is_active']
    fields = ['profile', 'character', 'is_active'] #('date_linked', 'date_unlinked'),

class CharacterInline(admin.TabularInline):
    model = CharacterRelationship.characters.through  # Access the ManyToMany through model
    extra = 1

@admin.register(CharacterRelationship)
class CharacterRelationshipAdmin(admin.ModelAdmin):
    list_display = [
        'relationship_type',
        'get_linked_characters',
        'last_updated',
    ]
    fields = [
        'relationship_type',
        'strength',
        'history',
        'biological',
        ('created_at', 'last_updated'),
    ]
    inlines = [CharacterInline]
    readonly_fields = ['created_at', 'last_updated']
    filter_horizontal = ['characters',]

    @admin.display(description="Characters")
    def get_linked_characters(self, obj):
        return ', '.join([str(char) for char in obj.get_members()])
    

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