from django.contrib import admin
from django.utils.html import format_html

from .models import Appointment, AppointmentSettings, BlockedRange, SlotLimit


@admin.register(AppointmentSettings)
class AppointmentSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "max_concurrent",
        "booking_window_days",
        "prevent_completion_on_insufficient_stock",
        "updated_at",
    )
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        """Prevent adding more than one settings instance."""
        return not AppointmentSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deleting the settings instance."""
        return False


@admin.register(BlockedRange)
class BlockedRangeAdmin(admin.ModelAdmin):
    list_display = ("start_at", "end_at", "reason", "created_at")
    list_filter = ("start_at", "end_at")
    search_fields = ("reason",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "start_at"


@admin.register(SlotLimit)
class SlotLimitAdmin(admin.ModelAdmin):
    list_display = ("date", "time_start", "time_end", "max_slots", "reason", "created_at")
    list_filter = ("date", "time_start", "created_at")
    search_fields = ("reason",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "date"

    fieldsets = (
        (None, {"fields": ("date", "time_start", "time_end")}),
        ("Slot Configuration", {"fields": ("max_slots", "reason")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    help_texts = {
        "max_slots": "Set to a number lower than the default max concurrent appointments to limit this specific time slot",
    }


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "service",
        "start_at",
        "end_at",
        "colored_status",
        "payment_state",
        "created_at",
    )
    list_filter = ("status", "payment_state", "start_at")
    search_fields = ("customer__email", "service__name", "notes")
    readonly_fields = ("created_at", "updated_at", "is_upcoming", "is_past")
    date_hierarchy = "start_at"
    autocomplete_fields = ["customer", "service"]

    fieldsets = (
        (None, {"fields": ("customer", "service")}),
        ("Timing", {"fields": ("start_at", "end_at", "is_upcoming", "is_past")}),
        ("Status", {"fields": ("status", "payment_state")}),
        ("Notes", {"fields": ("notes",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def colored_status(self, obj):
        """Color-code appointment status."""
        colors = {
            'completed': '#28a745',    # Green
            'confirmed': '#17a2b8',    # Blue
            'no_show': '#dc3545',      # Red
            'cancelled': '#6c757d',    # Gray
            'in_progress': '#ffc107',  # Yellow
            'pending': '#6f42c1',      # Purple
        }
        color = colors.get(obj.status, '#6c757d')

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    colored_status.short_description = 'Status'
