from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Payment(models.Model):
    """Payment model for demo payment transactions."""

    class Method(models.TextChoices):
        GCASH = "gcash", "GCash"
        PAYMAYA = "paymaya", "PayMaya"
        ONSITE = "onsite", "Onsite/Cash"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.CASCADE,
        related_name="payments",
        help_text="Linked appointment",
    )
    method = models.CharField(
        max_length=20,
        choices=Method.choices,
        default=Method.GCASH,
        help_text="Payment method",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Payment amount",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Payment status",
    )
    txn_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="Mock transaction ID (e.g., TXN-XXXXXX)",
    )
    notes = models.TextField(blank=True, help_text="Payment notes or error messages")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"{self.txn_id} - {self.method} - {self.status} (₱{self.amount})"

    @property
    def is_successful(self):
        """Check if payment was successful."""
        return self.status == self.Status.PAID
