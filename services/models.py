from django.db import models
from django.core.validators import MinValueValidator


class Service(models.Model):
    """Service model representing salon services."""

    name = models.CharField(max_length=200, help_text="Service name (e.g., Hair Rebond)")
    description = models.TextField(blank=True, help_text="Detailed service description")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Service price",
    )
    duration_minutes = models.IntegerField(
        validators=[MinValueValidator(1)], help_text="Duration in minutes"
    )
    image = models.ImageField(
        upload_to='services/', blank=True, null=True, help_text="Service image for display"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this service is available for booking"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return f"{self.name} (₱{self.price}, {self.duration_minutes}min)"


class ServiceItem(models.Model):
    """Link table defining inventory items required per service."""

    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="service_items"
    )
    item = models.ForeignKey(
        "inventory.Item", on_delete=models.CASCADE, related_name="service_links"
    )
    qty_per_service = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Quantity of this item consumed per service completion",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["service", "item"]
        verbose_name = "Service Item"
        verbose_name_plural = "Service Items"

    def __str__(self):
        return f"{self.service.name} → {self.item.name} ({self.qty_per_service})"
