from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Payment(models.Model):
    """Payment model for demo payment transactions."""

    class Method(models.TextChoices):
        GCASH = "gcash", "GCash"
        PAY = "pay", "Pay with Receipt"
        ONSITE = "onsite", "Onsite/Cash"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    class PaymentType(models.TextChoices):
        FULL_PAYMENT = "full", "Full Payment"
        DOWNPAYMENT = "downpayment", "Downpayment"

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
    payment_type = models.CharField(
        max_length=20,
        choices=PaymentType.choices,
        default=PaymentType.FULL_PAYMENT,
        help_text="Type of payment (full or downpayment)",
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
    receipt_image = models.ImageField(
        upload_to='payment_receipts/',
        blank=True,
        null=True,
        help_text="Receipt image for verification"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether payment has been verified by admin"
    )
    auto_verified = models.BooleanField(
        default=False,
        help_text="True if payment was auto-verified on receipt upload"
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When payment was verified"
    )
    verified_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_payments',
        help_text="Staff member who verified (null if auto-verified)"
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


class GCashQRCode(models.Model):
    """Model to store GCash QR code for receiving payments."""

    qr_image = models.ImageField(
        upload_to='gcash_qr/',
        help_text="GCash 'Receive Payment' QR code image"
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        default="GCash Receive Payment",
        help_text="Description for this QR code"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this QR code is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "GCash QR Code"
        verbose_name_plural = "GCash QR Codes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"GCash QR - {self.description} ({self.created_at.strftime('%Y-%m-%d')})"

    @classmethod
    def get_active_qr(cls):
        """Get the currently active QR code."""
        return cls.objects.filter(is_active=True).first()


class Receipt(models.Model):
    """Receipt generated after successful payment."""

    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='receipt',
        help_text="Associated payment"
    )
    html_content = models.TextField(help_text="HTML content of receipt")
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Receipt"
        verbose_name_plural = "Receipts"
        ordering = ["-generated_at"]

    def __str__(self):
        return f"Receipt for {self.payment.txn_id}"
