from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q, F, Avg
from django.db.models.functions import ExtractHour
from django.utils import timezone
from datetime import timedelta, datetime
from core.mixins import StaffOrAdminRequiredMixin
from appointments.models import Appointment
from payments.models import Payment
from inventory.models import Item
from services.models import Service
from .forecasting import SimpleETS, BusinessIntelligence


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
        context['today_revenue'] = revenue_today

        # Revenue this week
        revenue_week = all_payments.filter(
            created_at__gte=week_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['week_revenue'] = revenue_week

        # Revenue this month
        revenue_month = all_payments.filter(
            created_at__gte=month_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['month_revenue'] = revenue_month

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
            total_revenue=Sum('appointments__payments__amount', filter=Q(appointments__payments__status=Payment.Status.PAID))
        ).order_by('-booking_count')[:10]

        context['top_services'] = top_services

        # === INVENTORY ALERTS ===
        # Low stock items
        low_stock_items = Item.objects.filter(
            is_active=True,
            stock__lte=F('threshold')
        ).order_by('stock')

        context['low_stock_alerts'] = low_stock_items
        context['low_stock_count'] = low_stock_items.count()
        context['out_of_stock_count'] = low_stock_items.filter(stock=0).count()

        # === PAYMENT METHOD BREAKDOWN ===
        payment_methods = []
        for method_key, method_label in Payment.Method.choices:
            count = all_payments.filter(method=method_key).count()
            total = all_payments.filter(method=method_key).aggregate(
                total=Sum('amount')
            )['total'] or 0
            if count > 0:  # Only include methods that have been used
                payment_methods.append({
                    'method_display': method_label,
                    'count': count,
                    'total': total
                })

        context['payment_methods'] = payment_methods

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


class BusinessIntelligenceView(StaffOrAdminRequiredMixin, TemplateView):
    """Advanced business intelligence with forecasting and predictive analytics."""

    template_name = 'pages/analytics_business_intelligence.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()
        days_back = 90  # Analyze last 90 days
        forecast_days = 14  # Forecast next 14 days

        start_date = now - timedelta(days=days_back)

        # ===  REVENUE FORECASTING ===
        revenue_data = self._get_daily_revenue(start_date, now)
        revenue_values = [float(r['revenue']) for r in revenue_data]

        # Generate forecast
        revenue_forecast = SimpleETS.forecast_seasonal(
            revenue_values,
            periods=forecast_days,
            season_length=7,  # Weekly seasonality
            alpha=0.3,
            beta=0.1,
            gamma=0.1
        )

        context['revenue_forecast'] = [
            {
                'date': (now + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                'value': round(revenue_forecast[i], 2)
            }
            for i in range(forecast_days)
        ]
        context['total_predicted_revenue'] = sum(revenue_forecast)

        context['revenue_historical'] = revenue_data
        context['revenue_trend'] = BusinessIntelligence.detect_trend(revenue_values)

        # Revenue growth rate
        last_30_days = revenue_values[-30:] if len(revenue_values) >= 30 else revenue_values
        prev_30_days = revenue_values[-60:-30] if len(revenue_values) >= 60 else revenue_values[:len(revenue_values)//2]

        current_avg = sum(last_30_days) / len(last_30_days) if last_30_days else 0
        previous_avg = sum(prev_30_days) / len(prev_30_days) if prev_30_days else 0
        context['revenue_growth'] = BusinessIntelligence.calculate_growth_rate(current_avg, previous_avg)

        # === APPOINTMENT DEMAND FORECASTING ===
        appointment_data = self._get_daily_appointments(start_date, now)
        appointment_values = [r['count'] for r in appointment_data]

        appointment_forecast = SimpleETS.forecast_seasonal(
            appointment_values,
            periods=forecast_days,
            season_length=7,
            alpha=0.3,
            beta=0.1,
            gamma=0.1
        )

        context['appointment_forecast'] = [
            {
                'date': (now + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                'value': round(appointment_forecast[i], 1)
            }
            for i in range(forecast_days)
        ]

        context['appointment_historical'] = appointment_data
        context['appointment_trend'] = BusinessIntelligence.detect_trend(appointment_values)

        # === POPULAR SERVICES INSIGHTS ===
        popular_services = Service.objects.annotate(
            booking_count=Count('appointments', filter=Q(appointments__created_at__gte=start_date)),
            revenue=Sum('appointments__payments__amount', filter=Q(
                appointments__payments__status=Payment.Status.PAID,
                appointments__created_at__gte=start_date
            ))
        ).filter(booking_count__gt=0).order_by('-booking_count')[:10]

        context['popular_services'] = popular_services

        # === PEAK PERIODS ANALYSIS ===
        # Analyze by hour of day
        hourly_appointments = Appointment.objects.filter(
            created_at__gte=start_date
        ).annotate(
            hour=ExtractHour('start_at')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        context['peak_hours'] = list(hourly_appointments)

        # Analyze by day of week
        daily_appointments = []
        for i in range(7):
            day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][i]
            count = Appointment.objects.filter(
                created_at__gte=start_date,
                start_at__week_day=i+2  # Django week_day: 1=Sunday, 2=Monday, etc.
            ).count()
            daily_appointments.append({'day': day_name, 'count': count})

        context['peak_days'] = sorted(daily_appointments, key=lambda x: x['count'], reverse=True)

        # === INVENTORY INSIGHTS ===
        # Items needing restocking soon (based on usage trends)
        low_stock_items = Item.objects.filter(
            is_active=True,
            stock__lte=F('threshold') * 1.5  # 150% of threshold
        ).order_by('stock')[:10]

        context['items_needing_restock'] = low_stock_items

        # === KEY PERFORMANCE INDICATORS ===
        all_payments = Payment.objects.filter(status=Payment.Status.PAID)

        context['kpis'] = {
            'total_revenue': float(all_payments.aggregate(total=Sum('amount'))['total'] or 0),
            'total_appointments': Appointment.objects.count(),
            'total_customers': Appointment.objects.values('customer').distinct().count(),
            'avg_transaction': float(all_payments.aggregate(avg=Avg('amount'))['avg'] or 0),
            'completion_rate': self._calculate_completion_rate(),
            'customer_retention': self._calculate_retention_rate(start_date)
        }

        # === SEASONALITY ANALYSIS ===
        weekly_seasonality = BusinessIntelligence.calculate_seasonality_index(
            revenue_values,
            period_length=7
        )

        context['seasonality'] = [
            {
                'day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i],
                'index': round(weekly_seasonality[i], 2)
            }
            for i in range(7)
        ]

        # === FORECAST ACCURACY ===
        # If we have historical forecasts, we can compare them
        # For now, just provide general accuracy estimate
        if len(revenue_values) >= 30:
            # Use last 30 days for backtesting
            train_data = revenue_values[:-14]
            test_data = revenue_values[-14:]

            backtest_forecast = SimpleETS.forecast_seasonal(
                train_data,
                periods=14,
                season_length=7
            )

            accuracy = BusinessIntelligence.calculate_forecast_confidence(
                test_data,
                backtest_forecast[:len(test_data)]
            )

            context['forecast_accuracy'] = accuracy
        else:
            context['forecast_accuracy'] = {'mae': 0, 'mape': 0, 'accuracy': 85}

        return context

    def _get_daily_revenue(self, start_date, end_date):
        """Get daily revenue data."""
        daily_revenue = []
        current = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        while current <= end_date:
            day_end = current + timedelta(days=1)
            revenue = Payment.objects.filter(
                status=Payment.Status.PAID,
                created_at__gte=current,
                created_at__lt=day_end
            ).aggregate(total=Sum('amount'))['total'] or 0

            daily_revenue.append({
                'date': current.strftime('%Y-%m-%d'),
                'revenue': float(revenue)
            })
            current = day_end

        return daily_revenue

    def _get_daily_appointments(self, start_date, end_date):
        """Get daily appointment counts."""
        daily_appointments = []
        current = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        while current <= end_date:
            day_end = current + timedelta(days=1)
            count = Appointment.objects.filter(
                created_at__gte=current,
                created_at__lt=day_end
            ).count()

            daily_appointments.append({
                'date': current.strftime('%Y-%m-%d'),
                'count': count
            })
            current = day_end

        return daily_appointments

    def _calculate_completion_rate(self):
        """Calculate appointment completion rate."""
        total = Appointment.objects.count()
        if total == 0:
            return 0

        completed = Appointment.objects.filter(
            status=Appointment.Status.COMPLETED
        ).count()

        return round((completed / total) * 100, 1)

    def _calculate_retention_rate(self, since_date):
        """Calculate customer retention rate."""
        # Customers who have more than one appointment
        total_customers = Appointment.objects.filter(
            created_at__gte=since_date
        ).values('customer').distinct().count()

        if total_customers == 0:
            return 0

        repeat_customers = Appointment.objects.filter(
            created_at__gte=since_date
        ).values('customer').annotate(
            visit_count=Count('id')
        ).filter(visit_count__gt=1).count()

        return round((repeat_customers / total_customers) * 100, 1)
