from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.urls import reverse_lazy
import random
import string
from appointments.models import Appointment
from core.mixins import StaffOrAdminRequiredMixin
from .models import Payment, GCashQRCode
from .forms import GCashQRCodeForm


def generate_transaction_id():
    """Generate a mock transaction ID."""
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"TXN-{random_part}"


def simulate_demo_payment(payment_method):
    """
    Simulate payment processing based on settings.

    Returns:
        tuple: (is_successful: bool, message: str)
    """
    demo_mode = getattr(settings, 'DEMO_PAYMENT_MODE', 'deterministic')
    success_rate = getattr(settings, 'DEMO_PAYMENT_SUCCESS_RATE', 0.8)

    if demo_mode == 'always_success':
        return True, "Payment processed successfully"
    elif demo_mode == 'always_fail':
        return False, "Payment failed: Insufficient funds"
    elif demo_mode == 'random':
        if random.random() < success_rate:
            return True, "Payment processed successfully"
        else:
            return False, f"Payment failed: {random.choice(['Insufficient funds', 'Payment declined', 'Network error'])}"
    else:  # deterministic
        # GCash: always success
        # PayMaya: success based on rate
        # Onsite: always success
        if payment_method == Payment.Method.GCASH:
            return True, "GCash payment successful"
        elif payment_method == Payment.Method.PAYMAYA:
            if random.random() < success_rate:
                return True, "PayMaya payment successful"
            else:
                return False, "PayMaya payment failed: Transaction declined"
        else:  # onsite
            return True, "Cash payment recorded"


class PaymentInitiateView(LoginRequiredMixin, View):
    """Initiate payment for an appointment."""

    def get(self, request, appointment_id):
        """Show payment options."""
        appointment = get_object_or_404(Appointment, pk=appointment_id)

        # Check permissions
        if request.user.role == 'customer' and appointment.customer != request.user:
            messages.error(request, "You can only pay for your own appointments")
            return redirect('appointments:my_appointments')

        # Check if already paid
        if appointment.payment_state == Appointment.PaymentState.PAID:
            messages.info(request, "This appointment is already paid")
            return redirect('appointments:detail', pk=appointment_id)

        # Calculate payment amount and type
        service = appointment.service
        is_downpayment_required = service.requires_downpayment
        payment_amount = service.downpayment_amount if is_downpayment_required else service.price
        payment_type = Payment.PaymentType.DOWNPAYMENT if is_downpayment_required else Payment.PaymentType.FULL_PAYMENT

        # Get active GCash QR code
        active_qr = GCashQRCode.get_active_qr()

        context = {
            'appointment': appointment,
            'payment_methods': Payment.Method.choices,
            'payment_amount': payment_amount,
            'payment_type': payment_type,
            'is_downpayment_required': is_downpayment_required,
            'active_qr': active_qr,
        }
        return render(request, 'pages/payments_initiate.html', context)

    def post(self, request, appointment_id):
        """Process payment - customer uploads receipt for admin review."""
        appointment = get_object_or_404(Appointment, pk=appointment_id)

        # Check permissions
        if request.user.role == 'customer' and appointment.customer != request.user:
            messages.error(request, "You can only pay for your own appointments")
            return redirect('appointments:my_appointments')

        # Check if already paid
        if appointment.payment_state == Appointment.PaymentState.PAID:
            messages.info(request, "This appointment is already paid")
            return redirect('appointments:detail', pk=appointment_id)

        # Calculate payment details based on service requirements
        service = appointment.service
        is_downpayment_required = service.requires_downpayment
        payment_amount = service.downpayment_amount if is_downpayment_required else service.price
        payment_type = Payment.PaymentType.DOWNPAYMENT if is_downpayment_required else Payment.PaymentType.FULL_PAYMENT

        # Get receipt file
        receipt_file = request.FILES.get('receipt_image')
        if not receipt_file:
            messages.error(request, "Please upload a payment receipt")
            return redirect('payments:initiate', appointment_id=appointment_id)

        # Create payment record - AUTO-VERIFY on receipt upload
        with transaction.atomic():
            payment = Payment.objects.create(
                appointment=appointment,
                method=Payment.Method.PAY,
                amount=payment_amount,
                payment_type=payment_type,
                status=Payment.Status.PAID,  # Auto-verified!
                receipt_image=receipt_file,
                is_verified=True,  # Auto-verified on upload
                auto_verified=True,  # Mark as auto-verified
                verified_at=timezone.now(),  # Timestamp of verification
                verified_by=None,  # Auto-verified (not by staff)
                txn_id=generate_transaction_id(),
            )

            # Set appointment payment state to PAID immediately
            appointment.payment_state = Appointment.PaymentState.PAID

            payment.save()
            appointment.save()

        messages.success(
            request,
            f"✅ Payment confirmed! Transaction ID: {payment.txn_id}. Your appointment is now fully booked."
        )
        return redirect('payments:confirmation', payment_id=payment.pk)


class PaymentDetailView(LoginRequiredMixin, DetailView):
    """View payment details."""

    model = Payment
    template_name = 'pages/payments_detail.html'
    context_object_name = 'payment'

    def get_queryset(self):
        """Customers can only see their own payments."""
        qs = Payment.objects.select_related('appointment', 'appointment__service', 'appointment__customer')

        if self.request.user.role == 'customer':
            qs = qs.filter(appointment__customer=self.request.user)

        return qs


class PaymentListView(LoginRequiredMixin, ListView):
    """List payments - customers see their own, staff see all."""

    model = Payment
    template_name = 'pages/payments_list.html'
    context_object_name = 'payments'
    paginate_by = 20

    def get_queryset(self):
        """Filter based on user role."""
        qs = Payment.objects.select_related(
            'appointment',
            'appointment__service',
            'appointment__customer'
        ).order_by('-created_at')

        # Customers only see their own
        if self.request.user.role == 'customer':
            qs = qs.filter(appointment__customer=self.request.user)

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)

        # Filter by method
        method = self.request.GET.get('method')
        if method:
            qs = qs.filter(method=method)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['method_filter'] = self.request.GET.get('method', '')
        context['status_choices'] = Payment.Status.choices
        context['method_choices'] = Payment.Method.choices
        return context


class PaymentRetryView(LoginRequiredMixin, View):
    """Retry a failed payment."""

    def post(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        appointment = payment.appointment

        # Check permissions
        if request.user.role == 'customer' and appointment.customer != request.user:
            messages.error(request, "You can only retry your own payments")
            return redirect('appointments:my_appointments')

        # Can only retry failed payments
        if payment.status != Payment.Status.FAILED:
            messages.error(request, "Can only retry failed payments")
            return redirect('payments:detail', pk=pk)

        # Check if appointment is already paid via another payment
        if appointment.payment_state == Appointment.PaymentState.PAID:
            messages.info(request, "This appointment is already paid via another transaction")
            return redirect('payments:detail', pk=pk)

        # Create new payment attempt
        with transaction.atomic():
            new_payment = Payment.objects.create(
                appointment=appointment,
                method=payment.method,
                amount=payment.amount,
                status=Payment.Status.PENDING,
                txn_id=generate_transaction_id(),
                notes=f"Retry of {payment.txn_id}"
            )

            # Simulate payment processing
            is_successful, message = simulate_demo_payment(new_payment.method)

            if is_successful:
                new_payment.status = Payment.Status.PAID
                new_payment.notes += f" | {message}"
                appointment.payment_state = Appointment.PaymentState.PAID
                messages.success(request, f"Payment successful! Transaction ID: {new_payment.txn_id}")
            else:
                new_payment.status = Payment.Status.FAILED
                new_payment.notes += f" | {message}"
                appointment.payment_state = Appointment.PaymentState.FAILED
                messages.error(request, f"Payment failed again: {message}")

            new_payment.save()
            appointment.save()

        return redirect('payments:detail', pk=new_payment.pk)


class PaymentStatsView(StaffOrAdminRequiredMixin, TemplateView):
    """Staff/Admin view for payment statistics."""

    template_name = 'pages/payments_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Overall stats
        all_payments = Payment.objects.all()
        context['total_payments'] = all_payments.count()
        context['successful_payments'] = all_payments.filter(status=Payment.Status.PAID).count()
        context['failed_payments'] = all_payments.filter(status=Payment.Status.FAILED).count()
        context['pending_payments'] = all_payments.filter(status=Payment.Status.PENDING).count()

        # Revenue
        from django.db.models import Sum
        revenue = all_payments.filter(status=Payment.Status.PAID).aggregate(
            total=Sum('amount')
        )['total'] or 0
        context['total_revenue'] = revenue

        # By method
        context['payment_by_method'] = {
            method_key: all_payments.filter(method=method_key).count()
            for method_key, method_label in Payment.Method.choices
        }

        # Recent payments
        context['recent_payments'] = all_payments.select_related(
            'appointment', 'appointment__service', 'appointment__customer'
        ).order_by('-created_at')[:10]

        return context


class PaymentConfirmationView(LoginRequiredMixin, TemplateView):
    """Show payment confirmation with receipt after successful payment."""

    template_name = 'pages/payments_confirmation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment_id = self.kwargs.get('payment_id')
        payment = get_object_or_404(Payment, pk=payment_id)

        # Check permissions
        if self.request.user.role == 'customer' and payment.appointment.customer != self.request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied

        context['payment'] = payment
        context['appointment'] = payment.appointment
        context['receipt'] = payment.receipt if hasattr(payment, 'receipt') else None

        return context


class GenerateReceiptView(LoginRequiredMixin, View):
    """Generate and return receipt as downloadable HTML."""

    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, pk=payment_id)

        # Check permissions
        if request.user.role == 'customer' and payment.appointment.customer != request.user:
            messages.error(request, "You can only download your own receipts")
            return redirect('payments:list')

        appointment = payment.appointment

        # Generate HTML receipt
        receipt_html = self._generate_receipt_html(payment, appointment)

        from django.http import HttpResponse
        response = HttpResponse(receipt_html, content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="receipt_{payment.txn_id}.html"'

        return response

    def _generate_receipt_html(self, payment, appointment):
        """Generate professional receipt HTML."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Receipt {payment.txn_id}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            border: 1px solid #ddd;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 20px;
            margin-bottom: 20px;
        }}
        .receipt-title {{
            font-size: 28px;
            font-weight: bold;
            color: #333;
            margin: 0;
        }}
        .receipt-subtitle {{
            font-size: 12px;
            color: #999;
            margin: 5px 0 0 0;
        }}
        .section {{
            margin: 20px 0;
        }}
        .section-title {{
            font-weight: bold;
            font-size: 14px;
            color: #333;
            margin-bottom: 10px;
            border-bottom: 1px solid #e0e0e0;
            padding-bottom: 8px;
        }}
        .row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            font-size: 14px;
        }}
        .label {{
            color: #666;
            font-weight: 500;
        }}
        .value {{
            color: #333;
            text-align: right;
        }}
        .total-section {{
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
            border-left: 4px solid #4CAF50;
        }}
        .total-row {{
            display: flex;
            justify-content: space-between;
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background-color: #f0f0f0;
            padding: 12px;
            text-align: left;
            font-weight: bold;
            border-bottom: 2px solid #ddd;
            font-size: 13px;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
            font-size: 13px;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #999;
            font-size: 12px;
            border-top: 1px solid #e0e0e0;
            padding-top: 20px;
        }}
        .company-info {{
            font-weight: bold;
            color: #333;
            margin: 10px 0 5px 0;
        }}
        @media print {{
            body {{
                background-color: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
                border: none;
                padding: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <p class="receipt-title">Dreambook Salon</p>
            <p class="receipt-subtitle">Receipt</p>
        </div>

        <div class="section">
            <div class="row">
                <span class="label">Receipt Number</span>
                <span class="value">{payment.txn_id}</span>
            </div>
            <div class="row">
                <span class="label">Date</span>
                <span class="value">{payment.created_at.strftime('%B %d, %Y at %I:%M %p')}</span>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Customer Information</div>
            <div class="row">
                <span class="label">Name</span>
                <span class="value">{appointment.customer.get_full_name() or appointment.customer.email}</span>
            </div>
            <div class="row">
                <span class="label">Email</span>
                <span class="value">{appointment.customer.email}</span>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Service</th>
                    <th>Date & Time</th>
                    <th style="text-align: right;">Amount</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{appointment.service.name}</td>
                    <td>{appointment.start_at.strftime('%B %d, %Y %I:%M %p')} - {appointment.end_at.strftime('%I:%M %p')}</td>
                    <td style="text-align: right;">₱{payment.amount:,.2f}</td>
                </tr>
            </tbody>
        </table>

        <div class="total-section">
            <div class="total-row">
                <span>Total Paid</span>
                <span>₱{payment.amount:,.2f}</span>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Payment Information</div>
            <div class="row">
                <span class="label">Payment Method</span>
                <span class="value">{payment.get_method_display()}</span>
            </div>
            <div class="row">
                <span class="label">Payment Type</span>
                <span class="value">{payment.get_payment_type_display()}</span>
            </div>
            <div class="row">
                <span class="label">Status</span>
                <span class="value">{payment.get_status_display()}</span>
            </div>
        </div>

        <div class="footer">
            <p class="company-info">Dreambook Salon</p>
            <p>Premium Salon Management</p>
            <p>Thank you for your business!</p>
            <p style="margin-top: 20px; color: #ccc;">Generated on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>"""


