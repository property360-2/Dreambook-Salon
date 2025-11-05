from django.db import models
from django.core.validators import MinValueValidator


class Item(models.Model):
    """Inventory item model for tracking salon supplies."""

    name = models.CharField(max_length=200, unique=True, help_text="Item name")
    description = models.TextField(blank=True, help_text="Item description")
    unit = models.CharField(
        max_length=50,
        default="pcs",
        help_text="Unit of measurement (e.g., pcs, ml, kg)",
    )
    stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Current stock quantity",
    )
    threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=10,
        validators=[MinValueValidator(0)],
        help_text="Low stock alert threshold",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this item is actively tracked"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"

    def __str__(self):
        return f"{self.name} ({self.stock} {self.unit})"

    @property
    def is_low_stock(self):
        """Check if item is below threshold."""
        return self.stock <= self.threshold

    @property
    def stock_status(self):
        """Get stock status as string."""
        if self.stock <= 0:
            return "Out of Stock"
        elif self.is_low_stock:
            return "Low Stock"
        return "In Stock"
