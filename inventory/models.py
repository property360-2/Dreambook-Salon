from django.db import models
from django.core.validators import MinValueValidator


class Item(models.Model):
    """Inventory item model for tracking salon supplies."""

    class Category(models.TextChoices):
        HAIR = 'HAIR', 'Hair Products'
        NAILS = 'NAILS', 'Nail Products'
        SKIN = 'SKIN', 'Skin Products'
        SUPPLIES = 'SUPPLIES', 'General Supplies'
        OTHER = 'OTHER', 'Other'

    name = models.CharField(max_length=200, unique=True, help_text="Item name")
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
        help_text="Item category"
    )
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
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text="Expiration date (optional)"
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

    @property
    def expiry_status(self):
        """Get expiration status as string."""
        if not self.expiry_date:
            return None
        from django.utils import timezone
        from datetime import timedelta
        today = timezone.now().date()
        if self.expiry_date < today:
            return "Expired"
        elif self.expiry_date <= today + timedelta(days=30):
            return "Expiring Soon"
        return "Good"

    @property
    def is_expired(self):
        """Check if item is expired."""
        if not self.expiry_date:
            return False
        from django.utils import timezone
        return self.expiry_date < timezone.now().date()

    @property
    def is_expiring_soon(self):
        """Check if item is expiring within 30 days."""
        if not self.expiry_date:
            return False
        from django.utils import timezone
        from datetime import timedelta
        today = timezone.now().date()
        return today <= self.expiry_date <= today + timedelta(days=30)
