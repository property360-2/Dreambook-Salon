from django.db import models
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from decimal import Decimal


class Report(models.Model):
    """Cached report data to improve query performance."""

    class ReportType(models.TextChoices):
        REVENUE = "revenue", "Revenue Report"
        SERVICE_PERFORMANCE = "service_performance", "Service Performance"
        MONTHLY_TRENDS = "monthly_trends", "Monthly Trends"

    report_type = models.CharField(
        max_length=50,
        choices=ReportType.choices,
        help_text="Type of report"
    )
    title = models.CharField(max_length=255, help_text="Report title")
    description = models.TextField(blank=True, help_text="Report description")

    # Time period for the report
    start_date = models.DateField(help_text="Report period start")
    end_date = models.DateField(help_text="Report period end")

    # Summary metrics
    total_revenue = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text="Total revenue for period"
    )
    total_bookings = models.IntegerField(default=0, help_text="Total bookings")
    completed_bookings = models.IntegerField(default=0, help_text="Completed bookings")
    cancelled_bookings = models.IntegerField(default=0, help_text="Cancelled bookings")
    no_show_bookings = models.IntegerField(default=0, help_text="No-show bookings")

    # Refund tracking
    total_refunds = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text="Total refunds issued"
    )
    net_revenue = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text="Revenue minus refunds"
    )

    # Additional metrics
    average_booking_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Average booking amount"
    )
    completion_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Completion rate percentage (0-100)"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-generated_at"]
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        indexes = [
            models.Index(fields=["report_type", "-generated_at"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.start_date} to {self.end_date})"

    @classmethod
    def generate_revenue_report(cls, start_date, end_date):
        """Generate revenue report for the given period."""
        from appointments.models import Appointment
        from payments.models import Payment

        # Get all completed payments in the period
        payments = Payment.objects.filter(
            status=Payment.Status.PAID,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            appointment__status__in=[
                Appointment.Status.COMPLETED,
                Appointment.Status.IN_PROGRESS
            ]
        )

        total_revenue = payments.aggregate(Sum('amount'))['amount__sum'] or Decimal(0)

        # Get all bookings in period
        bookings = Appointment.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

        total_bookings = bookings.count()
        completed_bookings = bookings.filter(status=Appointment.Status.COMPLETED).count()
        cancelled_bookings = bookings.filter(status=Appointment.Status.CANCELLED).count()
        no_show_bookings = bookings.filter(status=Appointment.Status.NO_SHOW).count()

        # Calculate refunds
        total_refunds = bookings.filter(
            status=Appointment.Status.CANCELLED
        ).aggregate(Sum('refund_amount'))['refund_amount__sum'] or Decimal(0)

        net_revenue = total_revenue - total_refunds

        # Calculate averages
        paid_bookings = bookings.filter(payment_state=Appointment.PaymentState.PAID).count()
        average_value = total_revenue / paid_bookings if paid_bookings > 0 else Decimal(0)

        # Calculate completion rate
        completion_rate = (completed_bookings / total_bookings * 100) if total_bookings > 0 else Decimal(0)

        # Create or update report
        report, created = cls.objects.update_or_create(
            report_type=cls.ReportType.REVENUE,
            start_date=start_date,
            end_date=end_date,
            defaults={
                'title': f'Revenue Report: {start_date} to {end_date}',
                'description': f'Revenue and booking metrics for the period',
                'total_revenue': total_revenue,
                'total_bookings': total_bookings,
                'completed_bookings': completed_bookings,
                'cancelled_bookings': cancelled_bookings,
                'no_show_bookings': no_show_bookings,
                'total_refunds': total_refunds,
                'net_revenue': net_revenue,
                'average_booking_value': average_value,
                'completion_rate': completion_rate,
            }
        )

        return report

    @classmethod
    def generate_service_performance_report(cls, start_date, end_date):
        """Generate service performance report for the given period."""
        from appointments.models import Appointment

        bookings = Appointment.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

        total_bookings = bookings.count()
        completed_bookings = bookings.filter(status=Appointment.Status.COMPLETED).count()
        cancelled_bookings = bookings.filter(status=Appointment.Status.CANCELLED).count()
        no_show_bookings = bookings.filter(status=Appointment.Status.NO_SHOW).count()

        # Calculate revenue (paid bookings only)
        from payments.models import Payment
        paid_amount = Payment.objects.filter(
            status=Payment.Status.PAID,
            appointment__in=bookings,
            appointment__status__in=[
                Appointment.Status.COMPLETED,
                Appointment.Status.IN_PROGRESS
            ]
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)

        total_refunds = bookings.filter(
            status=Appointment.Status.CANCELLED
        ).aggregate(Sum('refund_amount'))['refund_amount__sum'] or Decimal(0)

        completion_rate = (completed_bookings / total_bookings * 100) if total_bookings > 0 else Decimal(0)

        report, created = cls.objects.update_or_create(
            report_type=cls.ReportType.SERVICE_PERFORMANCE,
            start_date=start_date,
            end_date=end_date,
            defaults={
                'title': f'Service Performance: {start_date} to {end_date}',
                'description': 'Performance metrics by service',
                'total_revenue': paid_amount,
                'total_bookings': total_bookings,
                'completed_bookings': completed_bookings,
                'cancelled_bookings': cancelled_bookings,
                'no_show_bookings': no_show_bookings,
                'total_refunds': total_refunds,
                'net_revenue': paid_amount - total_refunds,
                'completion_rate': completion_rate,
            }
        )

        return report


class ReportMetric(models.Model):
    """Detailed metrics for a specific report (e.g., per-service metrics)."""

    METRIC_TYPES = [
        ('service_bookings', 'Service Bookings'),
        ('service_revenue', 'Service Revenue'),
        ('daily_revenue', 'Daily Revenue'),
        ('payment_method', 'Payment Method'),
    ]

    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='metrics',
        help_text="Associated report"
    )
    metric_type = models.CharField(
        max_length=50,
        choices=METRIC_TYPES,
        help_text="Type of metric"
    )
    label = models.CharField(
        max_length=255,
        help_text="Label for this metric (e.g., service name, date, method)"
    )
    value = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text="Numeric value"
    )
    count = models.IntegerField(default=0, help_text="Count of items")
    percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Percentage of total"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-value"]
        verbose_name = "Report Metric"
        verbose_name_plural = "Report Metrics"

    def __str__(self):
        return f"{self.label}: {self.value}"
