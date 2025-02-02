from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile

# Register your models here.

admin.site.register(CustomUser, UserAdmin)

@admin.register(Profile)
class PlayerAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'name',
        'last_login',
        'level',
        'onboarding_step',
        'is_premium',    
    ]
    fields = [
        'user',
        'name',
        ('last_login', 'login_streak', 'login_streak_max'),
        'bio',
        ('xp', 'xp_next_level', 'xp_modifier'),
        'level',
        ('total_time', 'total_activities'),
        'onboarding_step',
        'is_premium',    
    ]
