from django.contrib import admin
from django.utils.timezone import now
from .models import MaintenanceWindow
import subprocess
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.urls import path
from asgiref.sync import async_to_sync

from gameplay.utils import send_group_message

@admin.action(description="Schedule maintenance tasks")
def schedule_window_tasks(modeladmin, request, queryset):
    for window in queryset:
        success = window.schedule_tasks()
        if success:
            modeladmin.message_user(request, f"Scheduled tasks for {window.name}.")
        else:
            modeladmin.message_user(request, f"Tasks already scheduled for {window.name}.", level="warning")

@admin.action(description="Delete scheduled tasks")
def delete_window_tasks(modeladmin, request, queryset):
    for window in queryset:
        window.delete_scheduled_tasks()
        modeladmin.message_user(request, f"Deleted tasks for {window.name}.")

@admin.action(description="Activate maintenance mode")
def activate_maintenance(modeladmin, request, queryset):
    for window in queryset:
        window.activate()
        modeladmin.message_user(request, f"Activated maintenance mode for {window.name}.")

@admin.action(description="Deactivate maintenance mode")
def deactivate_maintenance(modeladmin, request, queryset):
    subprocess.run(["python", "server_management/scripts/deactivate_maintenance.py"])
    modeladmin.message_user(request, "Maintenance mode deactivated.")


@admin.register(MaintenanceWindow)
class MaintenanceWindowAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'is_active', 'tasks_scheduled')
    ordering = ('start_time',)
    search_fields = ('name', 'description')
    readonly_fields = [
        'is_active',
    ]
    actions = [schedule_window_tasks, delete_window_tasks] #, activate_maintenance, deactivate_maintenance

    
    def activate_maintenance(self, request, maintenancewindow_id):
        window = self.get_object(request, maintenancewindow_id)
        if not window.is_active:
            window.activate_maintenance()
            profile = request.user.profile
            async_to_sync(send_group_message)("online_users", {"type": "action", "action": "refresh", "success": True})
            self.message_user(request, f"Maintenance window '{window.name}' now active!")
        else:    
            self.message_user(request, f"Maintenance window is already active: no action taken.")
        return redirect(f'/admin/server_management/maintenancewindow/{maintenancewindow_id}/change/')

    def deactivate_maintenance(self, request, maintenancewindow_id):
        window = self.get_object(request, maintenancewindow_id)
        if window.is_active:
            window.deactivate_maintenance()
            profile = request.user.profile
            async_to_sync(send_group_message)("online_users", {"type": "action", "action": "load-game", "success": True})
            self.message_user(request, f"Maintenance window '{window.name}' has finished. Enjoy playing!")
        else:
            self.message_user(request, f"Maintenance window is not activated: no action taken.")
        return redirect(f'/admin/server_management/maintenancewindow/{maintenancewindow_id}/change/')

    # Define custom admin URL
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:maintenancewindow_id>/activate/', self.admin_site.admin_view(self.activate_maintenance), name="activate_maintenance"),
            path('<int:maintenancewindow_id>/deactivate/', self.admin_site.admin_view(self.deactivate_maintenance), name="deactivate_maintenance"),
        ]
        return custom_urls + urls
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['activate_url'] = f'/admin/server_management/maintenancewindow/{object_id}/activate/'
        extra_context['deactivate_url'] = f'/admin/server_management/maintenancewindow/{object_id}/deactivate/'  # Add this line
        return super().change_view(request, object_id, form_url, extra_context)