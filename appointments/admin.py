from django.contrib import admin

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
        "status",
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
