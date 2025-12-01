from django.contrib import admin
from .models import DemandForecast, ForecastMetric


@admin.register(DemandForecast)
class DemandForecastAdmin(admin.ModelAdmin):
    """Admin interface for Demand Forecast model."""

    list_display = (
        'service',
        'forecast_type',
        'forecast_period',
        'forecast_start_date',
        'forecast_end_date',
        'periods_ahead',
        'trend_direction',
        'accuracy_score',
        'generated_at',
    )
    list_filter = ('forecast_type', 'forecast_period', 'trend_direction', 'generated_at')
    search_fields = ('service__name',)
    readonly_fields = (
        'forecast_values',
        'confidence_lower',
        'confidence_upper',
        'accuracy_mae',
        'accuracy_mape',
        'accuracy_score',
        'generated_at',
    )
    fieldsets = (
        ('Service & Type', {
            'fields': ('service', 'forecast_type', 'forecast_period')
        }),
        ('Forecast Period', {
            'fields': ('forecast_start_date', 'forecast_end_date', 'periods_ahead')
        }),
        ('Forecast Data', {
            'fields': ('forecast_values', 'confidence_lower', 'confidence_upper')
        }),
        ('Accuracy Metrics', {
            'fields': ('accuracy_mae', 'accuracy_mape', 'accuracy_score')
        }),
        ('Trend Analysis', {
            'fields': ('trend_direction', 'trend_strength', 'peak_day_of_week', 'peak_hour')
        }),
        ('Metadata', {
            'fields': ('generated_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ForecastMetric)
class ForecastMetricAdmin(admin.ModelAdmin):
    """Admin interface for Forecast Metric model."""

    list_display = ('label', 'metric_type', 'value', 'forecast', 'created_at')
    list_filter = ('metric_type', 'forecast__service', 'created_at')
    search_fields = ('label', 'forecast__service__name')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Metric Info', {
            'fields': ('forecast', 'metric_type', 'label')
        }),
        ('Value & Insight', {
            'fields': ('value', 'insight')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
