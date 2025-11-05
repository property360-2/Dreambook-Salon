from django.contrib import admin

from .models import Rule


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ("keyword", "is_active", "priority", "response_preview", "created_at")
    list_filter = ("is_active", "priority", "created_at")
    search_fields = ("keyword", "response")
    readonly_fields = ("created_at", "updated_at")
    list_editable = ("is_active", "priority")

    def response_preview(self, obj):
        """Show preview of response."""
        return obj.response[:50] + "..." if len(obj.response) > 50 else obj.response

    response_preview.short_description = "Response Preview"
