from django.contrib import admin

from .models import Service, ServiceItem


class ServiceItemInline(admin.TabularInline):
    """Inline admin for ServiceItem to manage inventory requirements."""

    model = ServiceItem
    extra = 1
    autocomplete_fields = ["item"]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "duration_minutes", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")

    def has_change_permission(self, request, obj=None):
        """Prevent viewing and editing individual service details."""
        return False

    def has_view_permission(self, request, obj=None):
        """Prevent viewing individual service details."""
        return False

    def has_add_permission(self, request):
        """Prevent adding new services."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deleting services."""
        return False


@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ("service", "item", "qty_per_service", "created_at")
    list_filter = ("service", "item")
    search_fields = ("service__name", "item__name")
    autocomplete_fields = ["service", "item"]
