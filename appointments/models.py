from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class AppointmentSettings(models.Model):
    """Singleton model for appointment configuration."""

    max_concurrent = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1)],
        help_text="Maximum concurrent appointments per time slot",
    )
    booking_window_days = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1)],
        help_text="How many days in advance customers can book",
    )
    prevent_completion_on_insufficient_stock = models.BooleanField(
        default=True,
        help_text="Prevent appointment completion if inventory is insufficient",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Appointment Settings"
        verbose_name_plural = "Appointment Settings"

    def __str__(self):
        return f"Settings (max: {self.max_concurrent}, window: {self.booking_window_days} days)"

    @classmethod
    def get_settings(cls):
        """Get or create singleton settings instance."""
        settings, _ = cls.objects.get_or_create(pk=1)
        return settings


class BlockedRange(models.Model):
    """Represents blocked time ranges when appointments cannot be made."""

    start_at = models.DateTimeField(help_text="Block start time")
    end_at = models.DateTimeField(help_text="Block end time")
    reason = models.CharField(
        max_length=255, blank=True, help_text="Reason for blocking (e.g., Holiday)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_at"]
        verbose_name = "Blocked Range"
        verbose_name_plural = "Blocked Ranges"

    def __str__(self):
        return f"Blocked: {self.start_at} - {self.end_at} ({self.reason})"

    def overlaps(self, start, end):
        """Check if this blocked range overlaps with given time range."""
        return start < self.end_at and end > self.start_at


class Appointment(models.Model):
    """Appointment model for booking services."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        NO_SHOW = "no_show", "No Show"
        CANCELLED = "cancelled", "Cancelled"

    class PaymentState(models.TextChoices):
        UNPAID = "unpaid", "Unpaid"
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments",
        help_text="Customer who booked the appointment",
    )
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.PROTECT,
        related_name="appointments",
        help_text="Service being booked",
    )
    start_at = models.DateTimeField(help_text="Appointment start time")
    end_at = models.DateTimeField(help_text="Appointment end time")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Current appointment status",
    )
    payment_state = models.CharField(
        max_length=20,
        choices=PaymentState.choices,
        default=PaymentState.UNPAID,
        help_text="Payment status",
    )
    notes = models.TextField(blank=True, help_text="Additional notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_at"]
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        indexes = [
            models.Index(fields=["start_at", "end_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.customer.email} - {self.service.name} @ {self.start_at}"

    @property
    def is_upcoming(self):
        """Check if appointment is in the future."""
        return self.start_at > timezone.now()

    @property
    def is_past(self):
        """Check if appointment is in the past."""
        return self.end_at < timezone.now()

    def save(self, *args, **kwargs):
        """Override save to auto-calculate end_at if not set."""
        if not self.end_at and self.service:
            from datetime import timedelta

            self.end_at = self.start_at + timedelta(minutes=self.service.duration_minutes)
        super().save(*args, **kwargs)
