from django.contrib import admin

from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ["profile", "name", "duration", "created_at"]
    list_filter = [
        "created_at",
        "duration",
    ]
    fields = [
        "name",
        "profile",
        "description",
        "duration",
        ("created_at", "last_updated"),
    ]
    readonly_fields = ["created_at", "last_updated"]
    date_hierarchy = "created_at"
    show_full_result_count = False
