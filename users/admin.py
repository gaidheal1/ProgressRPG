from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile
from character.models import PlayerCharacterLink

# Register your models here.

admin.site.register(CustomUser, UserAdmin)

@admin.register(Profile)
class PlayerAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'get_character',
        'name',
        'last_login',
        'user_created_at',
        'is_premium',
    ]
    list_filter = [
        'last_login',
        ]
    fields = [
        'user',
        'name',
        ('last_login', 'login_streak', 'login_streak_max'),
        'bio',
        ('xp', 'xp_next_level', 'xp_modifier'),
        'level',
        ('total_time', 'total_activities'),
        ('onboarding_step',
        'is_premium'),
    ]
    readonly_fields = [
        'last_login',
    ]
    search_fields = [
        'name',
        'get_character__name',
        ]

    def get_character(self, obj):
        return PlayerCharacterLink().get_character(obj)
    
    get_character.short_description = 'Character'

    def user_created_at(self, obj):
        return obj.user.created_at
    
    user_created_at.admin_order_field = 'user__created_at'  # Enables sorting
    user_created_at.short_description = 'User Created'  # Label in admin