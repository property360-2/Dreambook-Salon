from django.contrib import admin
from .models import Report, ReportMetric


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin interface for Report model."""

    list_display = (
        'title',
        'report_type',
        'start_date',
        'end_date',
        'total_revenue',
        'total_bookings',
        'completion_rate',
        'generated_at',
    )
    list_filter = ('report_type', 'generated_at', 'start_date')
    search_fields = ('title', 'description')
    readonly_fields = (
        'total_revenue',
        'total_bookings',
        'completed_bookings',
        'cancelled_bookings',
        'no_show_bookings',
        'total_refunds',
        'net_revenue',
        'average_booking_value',
        'completion_rate',
        'generated_at',
    )
    fieldsets = (
        ('Basic Info', {
            'fields': ('report_type', 'title', 'description')
        }),
        ('Period', {
            'fields': ('start_date', 'end_date')
        }),
        ('Summary Metrics', {
            'fields': (
                'total_revenue',
                'total_bookings',
                'completed_bookings',
                'cancelled_bookings',
                'no_show_bookings',
            )
        }),
        ('Financial Metrics', {
            'fields': (
                'total_refunds',
                'net_revenue',
                'average_booking_value',
            )
        }),
        ('Performance', {
            'fields': ('completion_rate',)
        }),
        ('Metadata', {
            'fields': ('generated_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReportMetric)
class ReportMetricAdmin(admin.ModelAdmin):
    """Admin interface for ReportMetric model."""

    list_display = ('label', 'metric_type', 'value', 'count', 'percentage', 'report')
    list_filter = ('metric_type', 'report__report_type', 'report__start_date')
    search_fields = ('label', 'report__title')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Metric Info', {
            'fields': ('report', 'metric_type', 'label')
        }),
        ('Values', {
            'fields': ('value', 'count', 'percentage')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
