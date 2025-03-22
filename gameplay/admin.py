from django.urls import path
from django.shortcuts import render
from django.contrib import admin
from django.http import HttpResponse
from django.template.response import TemplateResponse

from .models import Quest, QuestRequirement, QuestCompletion, Activity, ActivityTimer, QuestTimer, QuestResults, ServerMessage

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
        'duration_choices',
        'created_at',
        'frequency',
        ('intro_text',
        'outro_text'),
        'stages',
    ]
    list_display = [
        'name',
        'is_premium',
        'created_at',
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
    list_display = ['quest', 'xp_rate', 'coin_reward', 'dynamic_rewards']


@admin.register(QuestRequirement)
class QuestRequirementAdmin(admin.ModelAdmin):
    list_display = ['quest', 'prerequisite', 'times_required']



@admin.register(QuestCompletion)
class QuestCompletionAdmin(admin.ModelAdmin):
    list_display = ['character', 'quest', 'times_completed']
    fields = [
        'character', 
        'quest', 
        'times_completed',
        'last_completed',
    ]
    readonly_fields = ['last_completed']

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['profile', 'name', 'duration', 'created_at']
    list_filter = [
        'created_at',
        ]
    fields = [
        'profile',
        ('name', 
        'duration'), 
        ('created_at',
        'last_updated'),
    ]
    readonly_fields = ['created_at', 'last_updated']
    date_hierarchy = 'created_at'
    search_fields = ['profile__name']
    show_full_result_count = False
    
@admin.register(ActivityTimer)
class ActivityTimerAdmin(admin.ModelAdmin):
    list_display = ['profile', 'activity', 'elapsed_time', 'status']
    list_filter = ['status',]
    actions = ['pause_timers', 'reset_timers']

    def pause_timers(self, request, queryset):
        for timer in queryset:
            timer.pause()
        self.message_user(request, "Selected timers have been paused.")
    pause_timers.short_description = "Pause selected timers"

    def reset_timers(self, request, queryset):
        for timer in queryset:
            timer.reset()
        self.message_user(request, "Selected timers have been reset.")
    reset_timers.short_description = "Reset selected timers"

@admin.register(QuestTimer)
class QuestTimerAdmin(admin.ModelAdmin):
    list_display = ['character', 'elapsed_time', 'status']
    list_filter = ['status',]
    fields = [
        'character', 
        'quest', 
        'start_time', 
        'elapsed_time',
        'duration',
        'status',
    ]
    actions = ['pause_timers', 'reset_timers']

    def pause_timers(self, request, queryset):
        for timer in queryset:
            timer.pause()
        self.message_user(request, "Selected timers have been paused.")
    pause_timers.short_description = "Pause selected timers"

    def reset_timers(self, request, queryset):
        for timer in queryset:
            timer.reset()
        self.message_user(request, "Selected timers have been reset.")
    reset_timers.short_description = "Reset selected timers"


@admin.register(ServerMessage)
class ServerMessageAdmin(admin.ModelAdmin):
    list_display = ['profile', 'message', 'created_at']
    list_filter = [
        'profile',
        'created_at',
    ]
    fields = [
        'profile', 
        'type',
        'action',
        #'data',
        'message', 
        'created_at',
    ]
    readonly_fields = ['created_at']




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