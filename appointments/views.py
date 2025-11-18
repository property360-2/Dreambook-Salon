from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from .models import Appointment, AppointmentSettings, BlockedRange
from services.models import Service
from core.mixins import CustomerRequiredMixin, StaffOrAdminRequiredMixin


def check_availability(service, start_at, exclude_appointment_id=None):
    """
    Check if a service can be booked at the given time.

    Returns:
        tuple: (is_available: bool, reason: str or None)
    """
    settings = AppointmentSettings.get_settings()
    end_at = start_at + timedelta(minutes=service.duration_minutes)
    now = timezone.now()

    # Check 1: Not in the past
    if start_at < now:
        return False, "Cannot book appointments in the past"

    # Check 2: Within booking window
    max_future = now + timedelta(days=settings.booking_window_days)
    if start_at > max_future:
        return False, f"Cannot book more than {settings.booking_window_days} days in advance"

    # Check 3: Not in a blocked range
    blocked_ranges = BlockedRange.objects.filter(
        start_at__lt=end_at,
        end_at__gt=start_at
    )
    if blocked_ranges.exists():
        blocked = blocked_ranges.first()
        reason = f"Time slot blocked: {blocked.reason}" if blocked.reason else "Time slot is blocked"
        return False, reason

    # Check 4: Not exceeding max concurrent appointments
    # Find appointments that overlap with the requested time
    overlapping_appointments = Appointment.objects.filter(
        start_at__lt=end_at,
        end_at__gt=start_at,
        status__in=[
            Appointment.Status.PENDING,
            Appointment.Status.CONFIRMED,
            Appointment.Status.IN_PROGRESS
        ]
    )

    # Exclude current appointment if editing
    if exclude_appointment_id:
        overlapping_appointments = overlapping_appointments.exclude(id=exclude_appointment_id)

    concurrent_count = overlapping_appointments.count()
    if concurrent_count >= settings.max_concurrent:
        return False, f"Time slot full (max {settings.max_concurrent} concurrent appointments)"

    # Check 5: Verify inventory availability
    for service_item in service.service_items.all():
        if service_item.item.stock < service_item.qty_per_service:
            return False, f"Insufficient inventory: {service_item.item.name}"

    return True, None


class AppointmentBookingView(CustomerRequiredMixin, CreateView):
    """Customer booking view with availability checking."""

    model = Appointment
    template_name = 'pages/appointments_booking.html'
    fields = ['service', 'start_at', 'notes']
    success_url = reverse_lazy('appointments:my_appointments')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.filter(is_active=True)
        context['settings'] = AppointmentSettings.get_settings()

        # Pre-populate service if provided in URL query
        service_id = self.request.GET.get('service')
        if service_id:
            try:
                context['selected_service'] = Service.objects.get(id=service_id, is_active=True)
            except Service.DoesNotExist:
                pass

        return context

    def get_initial(self):
        """Pre-populate service field if provided in URL."""
        initial = super().get_initial()
        service_id = self.request.GET.get('service')
        if service_id:
            try:
                initial['service'] = Service.objects.get(id=service_id, is_active=True)
            except Service.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        appointment = form.save(commit=False)
        appointment.customer = self.request.user

        # Check availability
        is_available, reason = check_availability(
            appointment.service,
            appointment.start_at
        )

        if not is_available:
            messages.error(self.request, f"Booking failed: {reason}")
            return self.form_invalid(form)

        appointment.save()
        messages.success(
            self.request,
            f"Appointment booked successfully! {appointment.service.name} at {appointment.start_at.strftime('%Y-%m-%d %I:%M %p')}"
        )
        return redirect(self.success_url)


class MyAppointmentsView(CustomerRequiredMixin, ListView):
    """Customer's appointment list."""

    model = Appointment
    template_name = 'pages/appointments_my_list.html'
    context_object_name = 'appointments'
    paginate_by = 10

    def get_queryset(self):
        """Show only current user's appointments."""
        return Appointment.objects.filter(
            customer=self.request.user
        ).select_related('service').order_by('-start_at')


class AppointmentDetailView(LoginRequiredMixin, DetailView):
    """Appointment detail view - customers see their own, staff see all."""

    model = Appointment
    template_name = 'pages/appointments_detail.html'
    context_object_name = 'appointment'

    def get_queryset(self):
        """Customers can only see their own appointments."""
        qs = Appointment.objects.select_related('service', 'customer')

        # If customer, filter to only their appointments
        if self.request.user.role == 'customer':
            qs = qs.filter(customer=self.request.user)

        return qs


class AppointmentCancelView(LoginRequiredMixin, View):
    """Cancel an appointment (customers cancel their own, staff cancel any)."""

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)

        # Check permissions
        if request.user.role == 'customer' and appointment.customer != request.user:
            messages.error(request, "You can only cancel your own appointments")
            return redirect('appointments:my_appointments')

        # Can't cancel completed/no-show/already cancelled
        if appointment.status in [Appointment.Status.COMPLETED, Appointment.Status.NO_SHOW, Appointment.Status.CANCELLED]:
            messages.error(request, f"Cannot cancel appointment with status: {appointment.get_status_display()}")
            return redirect('appointments:detail', pk=pk)

        appointment.status = Appointment.Status.CANCELLED
        appointment.save()

        messages.success(request, "Appointment cancelled successfully")

        # Redirect based on user role
        if request.user.role == 'customer':
            return redirect('appointments:my_appointments')
        else:
            return redirect('appointments:staff_list')


class StaffAppointmentListView(StaffOrAdminRequiredMixin, ListView):
    """Staff/Admin view to see all appointments."""

    model = Appointment
    template_name = 'pages/appointments_staff_list.html'
    context_object_name = 'appointments'
    paginate_by = 20

    def get_queryset(self):
        """Show all appointments with filters."""
        qs = Appointment.objects.select_related('service', 'customer').order_by('-start_at')

        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)

        # Filter by date range
        date_filter = self.request.GET.get('date_filter', 'upcoming')
        now = timezone.now()

        if date_filter == 'upcoming':
            qs = qs.filter(start_at__gte=now)
        elif date_filter == 'past':
            qs = qs.filter(start_at__lt=now)
        elif date_filter == 'today':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            qs = qs.filter(start_at__gte=today_start, start_at__lt=today_end)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Appointment.Status.choices
        context['current_status'] = self.request.GET.get('status', '')
        context['date_filter'] = self.request.GET.get('date_filter', 'upcoming')
        return context


class AppointmentCompleteView(StaffOrAdminRequiredMixin, View):
    """Mark appointment as completed and deduct inventory."""

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        settings = AppointmentSettings.get_settings()

        # Can only complete in_progress appointments
        if appointment.status != Appointment.Status.IN_PROGRESS:
            messages.error(request, "Only in-progress appointments can be completed")
            return redirect('appointments:detail', pk=pk)

        # Check inventory if setting is enabled
        if settings.prevent_completion_on_insufficient_stock:
            insufficient_items = []
            for service_item in appointment.service.service_items.all():
                if service_item.item.stock < service_item.qty_per_service:
                    insufficient_items.append(service_item.item.name)

            if insufficient_items:
                messages.error(
                    request,
                    f"Cannot complete: Insufficient inventory for {', '.join(insufficient_items)}"
                )
                return redirect('appointments:detail', pk=pk)

        # Deduct inventory
        for service_item in appointment.service.service_items.all():
            item = service_item.item
            item.stock -= service_item.qty_per_service
            item.save()

        # Mark as completed
        appointment.status = Appointment.Status.COMPLETED
        appointment.save()

        messages.success(
            request,
            f"Appointment completed. Inventory deducted for {appointment.service.name}"
        )
        return redirect('appointments:detail', pk=pk)


class AppointmentUpdateStatusView(StaffOrAdminRequiredMixin, View):
    """Update appointment status (for staff/admin)."""

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        new_status = request.POST.get('status')

        if new_status not in dict(Appointment.Status.choices):
            messages.error(request, "Invalid status")
            return redirect('appointments:detail', pk=pk)

        # If marking as completed, use the complete view instead
        if new_status == Appointment.Status.COMPLETED:
            return AppointmentCompleteView.as_view()(request, pk=pk)

        appointment.status = new_status
        appointment.save()

        messages.success(request, f"Appointment status updated to {appointment.get_status_display()}")
        return redirect('appointments:detail', pk=pk)
