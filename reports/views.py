from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.db.models import Sum, Count, Q, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models.functions import TruncDate, TruncMonth

from appointments.models import Appointment
from payments.models import Payment
from services.models import Service
from .models import Report, ReportMetric


class StaffOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only staff can access reports."""

    def test_func(self):
        return self.request.user.is_staff


class ReportDashboardView(StaffOnlyMixin, TemplateView):
    """Dashboard showing key metrics and recent reports."""

    template_name = 'pages/reports_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Default to last 30 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        # Generate current period report
        report = Report.generate_revenue_report(start_date, end_date)

        # Get recent reports
        recent_reports = Report.objects.filter(
            report_type=Report.ReportType.REVENUE
        ).order_by('-generated_at')[:5]

        # Get upcoming bookings
        upcoming_bookings = Appointment.objects.filter(
            status=Appointment.Status.CONFIRMED,
            start_at__gte=timezone.now(),
            start_at__lte=timezone.now() + timedelta(days=7)
        ).count()

        # Get pending payments
        pending_payments = Payment.objects.filter(
            status=Payment.Status.PENDING
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)

        context.update({
            'report': report,
            'recent_reports': recent_reports,
            'upcoming_bookings': upcoming_bookings,
            'pending_payments': pending_payments,
            'start_date': start_date,
            'end_date': end_date,
        })

        return context


class RevenueReportView(StaffOnlyMixin, TemplateView):
    """Detailed revenue report with filters."""

    template_name = 'pages/reports_revenue.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get date range from GET params
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        if 'start_date' in self.request.GET:
            try:
                start_date = datetime.strptime(self.request.GET['start_date'], '%Y-%m-%d').date()
            except ValueError:
                pass

        if 'end_date' in self.request.GET:
            try:
                end_date = datetime.strptime(self.request.GET['end_date'], '%Y-%m-%d').date()
            except ValueError:
                pass

        # Generate report
        report = Report.generate_revenue_report(start_date, end_date)

        # Get daily revenue
        daily_revenue = Appointment.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status__in=[Appointment.Status.COMPLETED, Appointment.Status.IN_PROGRESS]
        ).values_list('created_at__date').annotate(
            revenue=Sum('refund_amount'),
            count=Count('id')
        ).order_by('created_at__date')

        # Get revenue by payment method
        payment_methods = Payment.objects.filter(
            status=Payment.Status.PAID,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).values('method').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')

        # Get top services by revenue
        top_services = Appointment.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status__in=[Appointment.Status.COMPLETED, Appointment.Status.IN_PROGRESS]
        ).values('service__name').annotate(
            revenue=Sum('refund_amount'),
            count=Count('id')
        ).order_by('-revenue')[:10]

        # Outstanding payments
        outstanding = Payment.objects.filter(
            status__in=[Payment.Status.PENDING, Payment.Status.FAILED],
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)

        context.update({
            'report': report,
            'start_date': start_date,
            'end_date': end_date,
            'daily_revenue': list(daily_revenue),
            'payment_methods': list(payment_methods),
            'top_services': list(top_services),
            'outstanding_payments': outstanding,
        })

        return context


class ServicePerformanceView(StaffOnlyMixin, TemplateView):
    """Service performance and utilization report."""

    template_name = 'pages/reports_service_performance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get date range from GET params
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        if 'start_date' in self.request.GET:
            try:
                start_date = datetime.strptime(self.request.GET['start_date'], '%Y-%m-%d').date()
            except ValueError:
                pass

        if 'end_date' in self.request.GET:
            try:
                end_date = datetime.strptime(self.request.GET['end_date'], '%Y-%m-%d').date()
            except ValueError:
                pass

        # Generate report
        report = Report.generate_service_performance_report(start_date, end_date)

        # Get metrics by service
        service_metrics = []
        services = Service.objects.filter(is_archived=False)

        for service in services:
            bookings = Appointment.objects.filter(
                service=service,
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            )

            total = bookings.count()
            completed = bookings.filter(status=Appointment.Status.COMPLETED).count()
            cancelled = bookings.filter(status=Appointment.Status.CANCELLED).count()
            no_show = bookings.filter(status=Appointment.Status.NO_SHOW).count()

            # Calculate revenue
            revenue = Payment.objects.filter(
                status=Payment.Status.PAID,
                appointment__in=bookings,
                appointment__status__in=[
                    Appointment.Status.COMPLETED,
                    Appointment.Status.IN_PROGRESS
                ]
            ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)

            completion_rate = (completed / total * 100) if total > 0 else 0

            service_metrics.append({
                'service': service,
                'total_bookings': total,
                'completed': completed,
                'cancelled': cancelled,
                'no_show': no_show,
                'revenue': revenue,
                'completion_rate': completion_rate,
                'avg_duration': service.duration_minutes,
            })

        # Sort by revenue
        service_metrics.sort(key=lambda x: x['revenue'], reverse=True)

        # Get booking status distribution
        status_dist = Appointment.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).values('status').annotate(count=Count('id')).order_by('-count')

        context.update({
            'report': report,
            'start_date': start_date,
            'end_date': end_date,
            'service_metrics': service_metrics,
            'status_distribution': list(status_dist),
        })

        return context


class GenerateReportAPIView(StaffOnlyMixin, View):
    """API endpoint to generate a report."""

    def post(self, request):
        report_type = request.POST.get('report_type', 'revenue')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid date format'}, status=400)

        if report_type == 'revenue':
            report = Report.generate_revenue_report(start_date, end_date)
        elif report_type == 'service_performance':
            report = Report.generate_service_performance_report(start_date, end_date)
        else:
            return JsonResponse({'error': 'Invalid report type'}, status=400)

        return JsonResponse({
            'id': report.id,
            'type': report.report_type,
            'title': report.title,
            'total_revenue': str(report.total_revenue),
            'total_bookings': report.total_bookings,
            'completion_rate': float(report.completion_rate),
        })


class ExportReportAPIView(StaffOnlyMixin, View):
    """API endpoint to export report data as JSON."""

    def get(self, request, report_id):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return JsonResponse({'error': 'Report not found'}, status=404)

        data = {
            'id': report.id,
            'type': report.report_type,
            'title': report.title,
            'period': f"{report.start_date} to {report.end_date}",
            'metrics': {
                'total_revenue': str(report.total_revenue),
                'total_bookings': report.total_bookings,
                'completed_bookings': report.completed_bookings,
                'cancelled_bookings': report.cancelled_bookings,
                'no_show_bookings': report.no_show_bookings,
                'total_refunds': str(report.total_refunds),
                'net_revenue': str(report.net_revenue),
                'average_booking_value': str(report.average_booking_value),
                'completion_rate': float(report.completion_rate),
            }
        }

        return JsonResponse(data)
