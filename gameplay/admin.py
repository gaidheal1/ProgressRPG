from django.urls import path
from django.shortcuts import render
from django.contrib import admin
from django.http import HttpResponse
from django.template.response import TemplateResponse
from .models import Quest, QuestRequirement, Character, QuestCompletion, Activity, ActivityTimer, QuestTimer, QuestResults

# Register your models here.
    
class QuestResultsInline(admin.TabularInline):
    model = QuestResults


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    fields = [
        'name',
        'description',
        ('canRepeat',
        'is_premium'),
        ('levelMin',
        'levelMax'),
        'duration',
        'created_at',
        'frequency',
        ('intro_text',
        'outro_text'),
        'stages',
    ]
    list_display = [
        'name',
        'description',
        'is_premium',
        'duration',
        'created_at',
        'levelMin',
        'levelMax',
    ]
    list_filter = [
        'created_at',
        'is_premium',
        'frequency',
        ]
    
    readonly_fields = [
        'created_at',
    ]
    inlines = [QuestResultsInline]
    
@admin.register(QuestResults)
class QuestResultsAdmin(admin.ModelAdmin):
    list_display = ['quest', 'xp_reward', 'coin_reward', 'dynamic_rewards', 'buffs']



@admin.register(QuestRequirement)
class QuestRequirementAdmin(admin.ModelAdmin):
    list_display = ['quest', 'prerequisite', 'times_required']

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    fields = [
        'name', 
        'backstory',
        'profile', 
        'current_quest', 
        'total_quests', 
        'gender', 
        'age', 
        ('dob',
         'dod'),
        'coins', 
        'location', 
        ('x_coordinate',
        'y_coordinate'),
        'is_npc',
    ]
    list_display = [
        'name', 
        'profile', 
        'current_quest', 
        'total_quests', 
        'gender', 
        'age', 
        'coins', 
        'location', 
        'is_npc'
        ]

@admin.register(QuestCompletion)
class QuestCompletionAdmin(admin.ModelAdmin):
    list_display = ['character', 'quest', 'times_completed']

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['profile', 'name', 'duration', 'created_at']
    
@admin.register(ActivityTimer)
class ActivityTimerAdmin(admin.ModelAdmin):
    list_display = ['profile', 'start_time', 'elapsed_time', 'is_running']
    actions = ['stop_timers', 'delete_timers']

    def stop_timers(self, request, queryset):
        queryset.update(is_running=False)
        self.message_user(request, "Selected timers have been stopped.")
    stop_timers.short_description = "Stop selected timers"

    def delete_timers(self, request, queryset):
        queryset.delete()
        self.message_user(request, "Selected timers have been deleted.")
    delete_timers.short_description = "Delete selected timers"

@admin.register(QuestTimer)
class QuestTimerAdmin(admin.ModelAdmin):
    list_display = ['character', 'start_time', 'elapsed_time', 'is_running']

    def stop_timers(self, request, queryset):
        queryset.update(is_running=False)
        self.message_user(request, "Selected timers have been stopped.")
    stop_timers.short_description = "Stop selected timers"

    def delete_timers(self, request, queryset):
        queryset.delete()
        self.message_user(request, "Selected timers have been deleted.")
    delete_timers.short_description = "Delete selected timers"

# class CustomAdminSite(admin.AdminSite):
#     #change_list_template = "admin/combined_timers.html"
#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('combined-timers/', self.admin_view(self.combined_timers_view), name='combined_timers'),
#         ]
#         return custom_urls + urls
    
#     def combined_timers_view(self, request):
#         activity_timers = ActivityTimer.objects.all()
#         quest_timers = QuestTimer.objects.all()
#         context = {
#             'title': 'Combined Timers',
#             'activity_timers': activity_timers,
#             'quest_timers': quest_timers,
#         }
#         return render(request, 'admin/combined_timers.html', context)
    
# custom_admin_site = CustomAdminSite(name='custom_admin')
# custom_admin_site.register(ActivityTimer)
# custom_admin_site.register(QuestTimer)