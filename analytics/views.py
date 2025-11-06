from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q, F, Avg
from django.utils import timezone
from datetime import timedelta
from core.mixins import StaffOrAdminRequiredMixin
from appointments.models import Appointment
from payments.models import Payment
from inventory.models import Item
from services.models import Service


class AnalyticsDashboardView(StaffOrAdminRequiredMixin, TemplateView):
    """Main analytics dashboard with revenue, services, and inventory insights."""

    template_name = 'pages/analytics_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Date ranges
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # === REVENUE STATS ===
        all_payments = Payment.objects.filter(status=Payment.Status.PAID)

        # Total revenue
        total_revenue = all_payments.aggregate(total=Sum('amount'))['total'] or 0
        context['total_revenue'] = total_revenue

        # Revenue today
        revenue_today = all_payments.filter(
            created_at__gte=today_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['revenue_today'] = revenue_today

        # Revenue this week
        revenue_week = all_payments.filter(
            created_at__gte=week_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['revenue_week'] = revenue_week

        # Revenue this month
        revenue_month = all_payments.filter(
            created_at__gte=month_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['revenue_month'] = revenue_month

        # === APPOINTMENT STATS ===
        all_appointments = Appointment.objects.all()

        context['total_appointments'] = all_appointments.count()
        context['completed_appointments'] = all_appointments.filter(
            status=Appointment.Status.COMPLETED
        ).count()
        context['pending_appointments'] = all_appointments.filter(
            status=Appointment.Status.PENDING
        ).count()
        context['cancelled_appointments'] = all_appointments.filter(
            status=Appointment.Status.CANCELLED
        ).count()

        # Upcoming appointments
        context['upcoming_appointments'] = all_appointments.filter(
            start_at__gte=now,
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        ).count()

        # === TOP SERVICES ===
        # Most booked services
        top_services = Service.objects.annotate(
            booking_count=Count('appointments'),
            completed_count=Count('appointments', filter=Q(appointments__status=Appointment.Status.COMPLETED)),
            revenue=Sum('appointments__payments__amount', filter=Q(appointments__payments__status=Payment.Status.PAID))
        ).order_by('-booking_count')[:10]

        context['top_services'] = top_services

        # === INVENTORY ALERTS ===
        # Low stock items
        low_stock_items = Item.objects.filter(
            is_active=True,
            stock__lte=F('threshold')
        ).order_by('stock')

        context['low_stock_items'] = low_stock_items
        context['low_stock_count'] = low_stock_items.count()
        context['out_of_stock_count'] = low_stock_items.filter(stock=0).count()

        # === PAYMENT METHOD BREAKDOWN ===
        payment_by_method = []
        for method_key, method_label in Payment.Method.choices:
            count = all_payments.filter(method=method_key).count()
            revenue = all_payments.filter(method=method_key).aggregate(
                total=Sum('amount')
            )['total'] or 0
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


class RevenueChartView(StaffOrAdminRequiredMixin, TemplateView):
    """Detailed revenue charts and trends."""

    template_name = 'pages/analytics_revenue.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get time period from query params (default: 30 days)
        period = self.request.GET.get('period', '30')
        try:
            days = int(period)
        except ValueError:
            days = 30

        now = timezone.now()
        start_date = now - timedelta(days=days)

        # Daily revenue data
        daily_revenue = []
        for i in range(days):
            day_start = (now - timedelta(days=days-i-1)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            revenue = Payment.objects.filter(
                status=Payment.Status.PAID,
                created_at__gte=day_start,
                created_at__lt=day_end
            ).aggregate(total=Sum('amount'))['total'] or 0

            daily_revenue.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'revenue': float(revenue)
            })

        context['daily_revenue'] = daily_revenue
        context['period'] = days

        # Revenue by service
        revenue_by_service = Service.objects.annotate(
            revenue=Sum(
                'appointments__payments__amount',
                filter=Q(
                    appointments__payments__status=Payment.Status.PAID,
                    appointments__payments__created_at__gte=start_date
                )
            )
        ).filter(revenue__isnull=False).order_by('-revenue')

        context['revenue_by_service'] = revenue_by_service

        # Total for period
        total_period_revenue = sum(item['revenue'] for item in daily_revenue)
        context['total_period_revenue'] = total_period_revenue

        # Average per day
        context['avg_daily_revenue'] = total_period_revenue / days if days > 0 else 0

        return context


class ServiceAnalyticsView(StaffOrAdminRequiredMixin, TemplateView):
    """Service performance analytics."""

    template_name = 'pages/analytics_services.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Service performance metrics
        services = Service.objects.annotate(
            total_bookings=Count('appointments'),
            completed_bookings=Count(
                'appointments',
                filter=Q(appointments__status=Appointment.Status.COMPLETED)
            ),
            cancelled_bookings=Count(
                'appointments',
                filter=Q(appointments__status=Appointment.Status.CANCELLED)
            ),
            total_revenue=Sum(
                'appointments__payments__amount',
                filter=Q(appointments__payments__status=Payment.Status.PAID)
            ),
            avg_rating=Avg('appointments__id')  # Placeholder - would use actual ratings if implemented
        ).order_by('-total_bookings')

        context['services'] = services

        # Completion rate
        for service in services:
            if service.total_bookings > 0:
                service.completion_rate = (service.completed_bookings / service.total_bookings) * 100
            else:
                service.completion_rate = 0

        return context


class InventoryAnalyticsView(StaffOrAdminRequiredMixin, TemplateView):
    """Inventory usage and alerts analytics."""

    template_name = 'pages/analytics_inventory.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # All inventory items with usage stats
        items = Item.objects.annotate(
            services_using=Count('service_links')
        ).order_by('stock')

        context['items'] = items

        # Critical alerts
        context['out_of_stock'] = items.filter(stock=0, is_active=True)
        context['low_stock'] = items.filter(
            stock__gt=0,
            stock__lte=F('threshold'),
            is_active=True
        )
        context['in_stock'] = items.filter(
            stock__gt=F('threshold'),
            is_active=True
        )

        # Stock value estimation (if we had cost field)
        # For now, just show quantities
        context['total_items'] = items.count()
        context['total_stock_units'] = items.aggregate(
            total=Sum('stock')
        )['total'] or 0

        return context
