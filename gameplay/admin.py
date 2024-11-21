from django.contrib import admin
from .models import Quest, QuestRequirement, Character, QuestCompletion

# Register your models here.
@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ['name',
        'description',
        'duration',
        'number_stages',
        'created_at',
        'levelMin',
        'levelMax',
        'canRepeat',
        'xpReward',
    ]

@admin.register(QuestRequirement)
class QuestRequirementAdmin(admin.ModelAdmin):
    list_display = ['quest', 'prerequisite', 'times_required']

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(QuestCompletion)
class QuestCompletionAdmin(admin.ModelAdmin):
    list_display = ['character', 'quest', 'times_completed']
