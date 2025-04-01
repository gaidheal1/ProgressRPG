from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile
from character.models import PlayerCharacterLink

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = [
        'email',
        'is_staff',
        'is_active',
    ]
    list_filter = [
        'is_staff',
        'is_active',
    ]
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ("Personal Info", {
            "fields": ("date_of_birth",)
        }),
        ('Permissions', {
            'classes': ('collapse',),
            'fields': ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'created_at')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ['email']
    ordering = ('email',)
    readonly_fields = ['created_at']

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
    
    fieldsets = (
        (None, {'fields': ('user', 'name')}),
        ("Login", {
            "fields": ('last_login', 'login_streak', 'login_streak_max', 'total_logins'),
        }),
        ('Levels/xp', {
            #'classes': ('collapse',),
            'fields': ('xp', 'xp_next_level', 'xp_modifier', 'level',),
        }),
        ('Metrics', {
            'fields': ('total_time', 'total_activities'),
        }),
        ('Other', {
            'fields': ('onboarding_step', 'is_premium'),
        }),
    )

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