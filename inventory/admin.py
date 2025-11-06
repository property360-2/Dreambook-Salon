from django.contrib import admin

from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "stock",
        "unit",
        "threshold",
        "stock_status",
        "is_active",
        "updated_at",
    )
    list_filter = ("is_active", "unit")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at", "stock_status")

    def stock_status(self, obj):
        """Display stock status with color coding."""
        return obj.stock_status

    stock_status.short_description = "Status"
