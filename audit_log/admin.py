"""Admin interface for Audit Logs"""
from django.contrib import admin
from django.utils.html import format_html
from .models import AuditLog, AuditLogFilter


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp_display', 'user', 'action_type_display', 'content_object_display', 'ip_address')
    list_filter = ('action_type', 'timestamp', 'user')
    search_fields = ('user__email', 'description', 'ip_address')
    readonly_fields = ('timestamp', 'ip_address', 'user_agent', 'changes_display')
    ordering = ['-timestamp']

    fieldsets = (
        ('Action Info', {
            'fields': ('user', 'action_type', 'timestamp'),
        }),
        ('Target Object', {
            'fields': ('content_type', 'object_id'),
        }),
        ('Changes', {
            'fields': ('changes_display',),
        }),
        ('Context', {
            'fields': ('description', 'ip_address', 'user_agent'),
        }),
    )

    def timestamp_display(self, obj):
        return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    timestamp_display.short_description = 'Timestamp'

    def action_type_display(self, obj):
        colors = {
            'CREATE': '#28a745',
            'UPDATE': '#ffc107',
            'DELETE': '#dc3545',
            'STATUS_CHANGE': '#17a2b8',
            'PAYMENT_UPDATE': '#6f42c1',
            'STOCK_ADJUSTMENT': '#20c997',
        }
        color = colors.get(obj.action_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_action_type_display()
        )
    action_type_display.short_description = 'Action'

    def content_object_display(self, obj):
        if obj.content_object:
            return f"{obj.content_type.name} #{obj.object_id}"
        return "-"
    content_object_display.short_description = 'Target'

    def changes_display(self, obj):
        return obj.get_changes_display()
    changes_display.short_description = 'Changes'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(AuditLogFilter)
class AuditLogFilterAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at', 'is_default')
    list_filter = ('is_default', 'created_at')
    search_fields = ('name', 'user__email')
