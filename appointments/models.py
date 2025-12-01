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


class SlotLimit(models.Model):
    """
    Represents custom max concurrent slot limits for specific date/time combinations.
    Allows admins to limit the number of concurrent appointments for specific times.
    """

    date = models.DateField(help_text="The date for this slot limit")
    time_start = models.TimeField(help_text="Start time (e.g., 09:00)")
    time_end = models.TimeField(help_text="End time (e.g., 09:30)")
    max_slots = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Maximum concurrent appointments for this time slot",
    )
    reason = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional reason for the slot limit (e.g., Staff absent)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "time_start"]
        verbose_name = "Slot Limit"
        verbose_name_plural = "Slot Limits"
        unique_together = ("date", "time_start", "time_end")
        indexes = [
            models.Index(fields=["date", "time_start", "time_end"]),
        ]

    def __str__(self):
        return f"{self.date} {self.time_start}-{self.time_end}: {self.max_slots} slots"


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
        default=Status.CONFIRMED,
        help_text="Current appointment status",
    )
    payment_state = models.CharField(
        max_length=20,
        choices=PaymentState.choices,
        default=PaymentState.UNPAID,
        help_text="Payment status",
    )
    notes = models.TextField(blank=True, help_text="Additional notes")
    cancelled_at = models.DateTimeField(
        blank=True, null=True, help_text="Timestamp of cancellation"
    )
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="cancelled_appointments",
        help_text="User who cancelled the appointment"
    )
    cancellation_reason = models.TextField(
        blank=True, help_text="Reason for cancellation"
    )
    refund_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        validators=[MinValueValidator(0)],
        help_text="Amount refunded to customer"
    )
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

    def calculate_refund(self):
        """
        Calculate refund amount based on cancellation timing.

        Returns:
            tuple: (refund_percentage: float, refund_amount: Decimal)
        """
        from datetime import timedelta

        now = timezone.now()
        hours_until = (self.start_at - now).total_seconds() / 3600

        # Get payment amount
        from payments.models import Payment
        payment = Payment.objects.filter(
            appointment=self,
            status=Payment.Status.PAID
        ).first()

        if not payment:
            return 0, 0

        # Refund logic
        if hours_until > 48:
            # More than 48 hours before: 100% refund
            percentage = 100
        elif hours_until > 24:
            # 24-48 hours before: 50% refund
            percentage = 50
        else:
            # Less than 24 hours: No refund
            percentage = 0

        refund_amt = payment.amount * (percentage / 100)
        return percentage, refund_amt

    def cancel(self, cancelled_by, reason=""):
        """
        Cancel the appointment and calculate refund.

        Args:
            cancelled_by: User who cancelled the appointment
            reason: Reason for cancellation
        """
        # Calculate refund
        percentage, refund_amt = self.calculate_refund()

        # Update appointment
        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancelled_by = cancelled_by
        self.cancellation_reason = reason
        self.refund_amount = refund_amt
        self.save()

        return percentage, refund_amt
