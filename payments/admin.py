from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "txn_id",
        "appointment",
        "method",
        "amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "method", "created_at")
    search_fields = ("txn_id", "appointment__customer__email", "notes")
    readonly_fields = ("created_at", "updated_at", "is_successful")
    autocomplete_fields = ["appointment"]

    fieldsets = (
        (None, {"fields": ("appointment", "txn_id")}),
        ("Payment Details", {"fields": ("method", "amount", "status")}),
        ("Additional Info", {"fields": ("notes", "is_successful")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
