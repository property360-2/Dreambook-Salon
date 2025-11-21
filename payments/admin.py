from django.contrib import admin

from .models import Payment, GCashQRCode


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "txn_id",
        "appointment",
        "method",
        "payment_type",
        "amount",
        "status",
        "is_verified",
        "created_at",
    )
    list_filter = ("status", "method", "payment_type", "is_verified", "created_at")
    search_fields = ("txn_id", "appointment__customer__email", "notes")
    readonly_fields = ("created_at", "updated_at", "is_successful", "receipt_image_preview")
    autocomplete_fields = ["appointment"]
    actions = ["verify_payment"]

    fieldsets = (
        (None, {"fields": ("appointment", "txn_id")}),
        ("Payment Details", {"fields": ("method", "payment_type", "amount", "status")}),
        ("Receipt & Verification", {"fields": ("receipt_image", "receipt_image_preview", "is_verified")}),
        ("Additional Info", {"fields": ("notes", "is_successful")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def receipt_image_preview(self, obj):
        """Display a preview of the receipt image."""
        if obj.receipt_image:
            return f'<img src="{obj.receipt_image.url}" style="max-width: 200px; max-height: 200px;" />'
        return "No receipt uploaded"
    receipt_image_preview.allow_tags = True
    receipt_image_preview.short_description = "Receipt Preview"

    def verify_payment(self, request, queryset):
        """Admin action to verify pending payments and confirm appointments."""
        from django.db import transaction
        from appointments.models import Appointment

        verified_count = 0
        for payment in queryset:
            if payment.status == Payment.Status.PENDING:
                with transaction.atomic():
                    # Mark payment as verified and paid
                    payment.status = Payment.Status.PAID
                    payment.is_verified = True
                    payment.save()

                    # Update appointment payment state
                    appointment = payment.appointment
                    appointment.payment_state = Appointment.PaymentState.PAID

                    # Auto-confirm appointment if downpayment
                    if payment.payment_type == Payment.PaymentType.DOWNPAYMENT:
                        appointment.status = Appointment.Status.CONFIRMED

                    appointment.save()
                    verified_count += 1

        self.message_user(
            request,
            f"{verified_count} payment(s) verified successfully. Associated appointments have been updated."
        )
    verify_payment.short_description = "Verify selected payments and confirm appointments"


@admin.register(GCashQRCode)
class GCashQRCodeAdmin(admin.ModelAdmin):
    list_display = ("description", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("description",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("GCash QR Code", {"fields": ("description", "qr_image", "is_active")}),
        ("Info", {"fields": ("created_at", "updated_at")}),
    )

    def save_model(self, request, obj, form, change):
        """Auto-deactivate other QR codes when activating a new one"""
        if obj.is_active:
            GCashQRCode.objects.exclude(pk=obj.pk if obj.pk else None).update(is_active=False)
        super().save_model(request, obj, form, change)
