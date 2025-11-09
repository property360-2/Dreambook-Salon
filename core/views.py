from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta

from .forms import CustomerRegistrationForm, EmailAuthenticationForm
from .mixins import StaffOrAdminRequiredMixin
from appointments.models import Appointment
from payments.models import Payment
from inventory.models import Item
from services.models import Service


class HomeView(TemplateView):
    """Landing page - routes to dashboard for staff/admin, business page for others."""
    template_name = "pages/home.html"

    def dispatch(self, request, *args, **kwargs):
        # Redirect staff/admin to dashboard
        if request.user.is_authenticated and request.user.role in ['ADMIN', 'STAFF']:
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get actual featured services from database
        featured_services = Service.objects.filter(is_active=True)[:3]
        context['featured_services'] = featured_services

        return context


class DashboardView(StaffOrAdminRequiredMixin, TemplateView):
    """Comprehensive dashboard for admin and staff with all business metrics."""
    template_name = "pages/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Date ranges
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # === REVENUE STATS ===
        all_payments = Payment.objects.filter(status=Payment.Status.PAID)

        context['total_revenue'] = all_payments.aggregate(total=Sum('amount'))['total'] or 0
        context['revenue_today'] = all_payments.filter(
            created_at__gte=today_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['revenue_week'] = all_payments.filter(
            created_at__gte=week_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['revenue_month'] = all_payments.filter(
            created_at__gte=month_ago
        ).aggregate(total=Sum('amount'))['total'] or 0

        # === APPOINTMENT STATS ===
        all_appointments = Appointment.objects.all()

        context['total_appointments'] = all_appointments.count()
        context['completed_appointments'] = all_appointments.filter(
            status=Appointment.Status.COMPLETED
        ).count()
        context['pending_appointments'] = all_appointments.filter(
            status=Appointment.Status.PENDING
        ).count()
        context['confirmed_appointments'] = all_appointments.filter(
            status=Appointment.Status.CONFIRMED
        ).count()
        context['cancelled_appointments'] = all_appointments.filter(
            status=Appointment.Status.CANCELLED
        ).count()

        # Upcoming appointments (today and future)
        context['upcoming_appointments'] = all_appointments.filter(
            start_at__gte=now,
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        ).order_by('start_at')[:5]

        # Today's appointments
        tomorrow_start = today_start + timedelta(days=1)
        context['today_appointments'] = all_appointments.filter(
            start_at__gte=today_start,
            start_at__lt=tomorrow_start
        ).order_by('start_at')

        # === SERVICES STATS ===
        context['total_services'] = Service.objects.filter(is_active=True).count()
        context['inactive_services'] = Service.objects.filter(is_active=False).count()

        # Top services by bookings
        top_services = Service.objects.annotate(
            booking_count=Count('appointment'),
            completed_count=Count('appointment', filter=Q(appointment__status=Appointment.Status.COMPLETED)),
            revenue=Sum('appointment__payment__amount', filter=Q(appointment__payment__status=Payment.Status.PAID))
        ).order_by('-booking_count')[:5]
        context['top_services'] = top_services

        # === INVENTORY STATS ===
        all_items = Item.objects.filter(is_active=True)
        context['total_inventory_items'] = all_items.count()

        low_stock_items = all_items.filter(stock__lte=F('threshold')).order_by('stock')
        context['low_stock_items'] = low_stock_items[:5]
        context['low_stock_count'] = low_stock_items.count()
        context['out_of_stock_count'] = all_items.filter(stock=0).count()

        # === PAYMENT STATS ===
        context['total_payments'] = all_payments.count()
        context['pending_payments'] = Payment.objects.filter(status=Payment.Status.PENDING).count()

        # Payment method breakdown
        payment_by_method = []
        for method_key, method_label in Payment.Method.choices:
            count = all_payments.filter(method=method_key).count()
            revenue = all_payments.filter(method=method_key).aggregate(
                total=Sum('amount')
            )['total'] or 0
            if count > 0:
                payment_by_method.append({
                    'method': method_label,
                    'count': count,
                    'revenue': revenue
                })
        context['payment_by_method'] = payment_by_method

        # === RECENT ACTIVITY ===
        context['recent_appointments'] = Appointment.objects.select_related(
            'service', 'customer'
        ).order_by('-created_at')[:5]

        context['recent_payments'] = Payment.objects.select_related(
            'appointment', 'appointment__service'
        ).order_by('-created_at')[:5]

        return context


class EmailLoginView(LoginView):
    template_name = "pages/auth_login.html"
    form_class = EmailAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "You're signed in. Welcome back!")
        return super().form_valid(form)


class EmailLogoutView(LogoutView):
    next_page = reverse_lazy("core:login")

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "You've been signed out.")
        return super().dispatch(request, *args, **kwargs)


class CustomerRegistrationView(FormView):
    template_name = "pages/auth_register.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Welcome aboard! You're now signed in.")
        return super().form_valid(form)
