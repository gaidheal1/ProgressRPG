from django.contrib import admin
from .models import Character, PlayerCharacterLink
# Register your models here.


class LinkInline(admin.TabularInline):
    model = PlayerCharacterLink


#@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    # def current_player(self, obj):
    #     link = PlayerCharacterLink.objects.filter(character=obj, is_active=True).first()
    #     return link.profile.name if link else 'No player linked'
    
    # current_player.short_description = 'Current Player'

    fields = [
        'first_name', 
        'last_name',
        'name',
        #'current_player',
        'backstory',
        'parents',
        'gender', 
        ('is_pregnant',
        'pregnancy_start_date',
        'pregnancy_due_date'),
        ('dob',
        'dod'),
        'cause_of_death',
        'coins',
        'reputation',
        ('location', 
        'x_coordinate',
        'y_coordinate'),
        'is_npc',
        'total_quests',
    ]
    list_display = [
        'name',
        #'current_player',
        'is_npc',
        'dob',

        ]
    inlines = [LinkInline]

admin.site.register(Character, CharacterAdmin)

@admin.register(PlayerCharacterLink)
class PlayerCharacterLinkAdmin(admin.ModelAdmin):
    list_display = ['profile', 'character', 'is_active']
    fields = ['profile', 'character', 'is_active'] #('date_linked', 'date_unlinked'),
