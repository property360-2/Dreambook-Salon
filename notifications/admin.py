from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for notifications."""

    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Notification Info', {
            'fields': ('user', 'notification_type', 'title', 'message', 'link')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        """Disable manual creation via admin; use create_notification() method instead."""
        return False
