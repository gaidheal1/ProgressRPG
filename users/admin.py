from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Player

# Register your models here.

admin.site.register(CustomUser, UserAdmin)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio', 'profile_picture', 'xp', 'level', 'total_time', 'total_activities']
    