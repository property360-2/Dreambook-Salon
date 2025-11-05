from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.db import transaction
import random
import string
from appointments.models import Appointment
from core.mixins import StaffOrAdminRequiredMixin
from .models import Payment


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

        context = {
            'appointment': appointment,
            'payment_methods': Payment.Method.choices,
        }
        return render(request, 'pages/payments_initiate.html', context)

    def post(self, request, appointment_id):
        """Process payment."""
        appointment = get_object_or_404(Appointment, pk=appointment_id)

        # Check permissions
        if request.user.role == 'customer' and appointment.customer != request.user:
            messages.error(request, "You can only pay for your own appointments")
            return redirect('appointments:my_appointments')

        # Check if already paid
        if appointment.payment_state == Appointment.PaymentState.PAID:
            messages.info(request, "This appointment is already paid")
            return redirect('appointments:detail', pk=appointment_id)

        payment_method = request.POST.get('payment_method')
        if payment_method not in dict(Payment.Method.choices):
            messages.error(request, "Invalid payment method")
            return redirect('payments:initiate', appointment_id=appointment_id)

        # Create payment record
        with transaction.atomic():
            payment = Payment.objects.create(
                appointment=appointment,
                method=payment_method,
                amount=appointment.service.price,
                status=Payment.Status.PENDING,
                txn_id=generate_transaction_id(),
            )

            # Simulate payment processing
            is_successful, message = simulate_demo_payment(payment_method)

            if is_successful:
                payment.status = Payment.Status.PAID
                payment.notes = message
                appointment.payment_state = Appointment.PaymentState.PAID
                messages.success(request, f"Payment successful! Transaction ID: {payment.txn_id}")
            else:
                payment.status = Payment.Status.FAILED
                payment.notes = message
                appointment.payment_state = Appointment.PaymentState.FAILED
                messages.error(request, f"Payment failed: {message}")

            payment.save()
            appointment.save()

        return redirect('payments:detail', pk=payment.pk)


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


class PaymentStatsView(LoginRequiredMixin, StaffOrAdminRequiredMixin, TemplateView):
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
