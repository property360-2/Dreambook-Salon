"""Admin interface for Audit Logs"""
import json
from django.contrib import admin
from django.utils.html import format_html
from .models import AuditLog, AuditLogFilter


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp_display', 'action_type', 'actor_email', 'target_display', 'request_method', 'status_code', 'ip_address')
    list_filter = ('timestamp', 'user', 'action_type', 'source', 'request_method')
    search_fields = ('user__email', 'actor_email', 'actor_name', 'target_repr', 'description', 'request_path', 'ip_address')
    readonly_fields = (
        'timestamp',
        'ip_address',
        'user_agent',
        'changes_display',
        'action_type',
        'actor_email',
        'actor_name',
        'actor_role',
        'source',
        'request_method',
        'request_path',
        'route_name',
        'status_code',
        'target_repr',
        'target_type',
        'metadata_display',
    )
    ordering = ['-timestamp']

    fieldsets = (
        ('Action Info', {
            'fields': ('user', 'actor_name', 'actor_email', 'actor_role', 'source', 'action_type', 'timestamp'),
        }),
        ('Target Object', {
            'fields': ('target_repr', 'target_type', 'content_type', 'object_id'),
        }),
        ('Request Context', {
            'fields': ('request_method', 'request_path', 'route_name', 'status_code', 'ip_address', 'user_agent', 'metadata_display'),
        }),
        ('Changes', {
            'fields': ('changes_display',),
        }),
        ('Context', {
            'fields': ('description',),
        }),
    )

    def timestamp_display(self, obj):
        return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    timestamp_display.short_description = 'Timestamp'

    def target_display(self, obj):
        if obj.target_repr:
            return obj.target_repr
        if obj.content_object:
            return f"{obj.content_type.name} #{obj.object_id}"
        return "-"
    target_display.short_description = 'Target'

    def changes_display(self, obj):
        return obj.get_changes_display()
    changes_display.short_description = 'Changes'

    def metadata_display(self, obj):
        if not obj.metadata:
            return "-"
        return format_html("<pre style='white-space: pre-wrap;'>{}</pre>", json.dumps(obj.metadata, indent=2, sort_keys=True))
    metadata_display.short_description = 'Metadata'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(AuditLogFilter)
class AuditLogFilterAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at', 'is_default')
    list_filter = ('is_default', 'created_at')
    search_fields = ('name', 'user__email')
