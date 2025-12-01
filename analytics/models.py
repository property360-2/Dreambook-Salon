from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from datetime import datetime, timedelta
from decimal import Decimal


class DemandForecast(models.Model):
    """Stores demand forecasts for services."""

    class ForecastType(models.TextChoices):
        SIMPLE = "simple", "Simple Exponential Smoothing"
        TREND = "trend", "Trend (Holt's Method)"
        SEASONAL = "seasonal", "Seasonal (Holt-Winters)"

    class ForecastPeriod(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"

    service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE,
        related_name="forecasts",
        help_text="Service being forecasted"
    )
    forecast_type = models.CharField(
        max_length=20,
        choices=ForecastType.choices,
        default=ForecastType.SEASONAL,
        help_text="Forecasting method used"
    )
    forecast_period = models.CharField(
        max_length=20,
        choices=ForecastPeriod.choices,
        default=ForecastPeriod.DAILY,
        help_text="Period granularity"
    )

    # Forecast period
    forecast_start_date = models.DateField(help_text="Start date of forecast")
    forecast_end_date = models.DateField(help_text="End date of forecast")
    periods_ahead = models.IntegerField(
        default=7,
        validators=[MinValueValidator(1)],
        help_text="Number of periods forecasted ahead"
    )

    # Forecast data (stored as JSON-like structure)
    forecast_values = models.TextField(help_text="Comma-separated forecast values")  # "10,12,15,8,11,..."
    confidence_lower = models.TextField(blank=True, help_text="Lower confidence bound values")
    confidence_upper = models.TextField(blank=True, help_text="Upper confidence bound values")

    # Forecast metrics
    accuracy_mae = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0)],
        help_text="Mean Absolute Error"
    )
    accuracy_mape = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0)],
        help_text="Mean Absolute Percentage Error"
    )
    accuracy_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), ],
        help_text="Overall accuracy score (0-100)"
    )

    # Trend analysis
    trend_direction = models.CharField(
        max_length=20,
        choices=[
            ('increasing', 'Increasing'),
            ('decreasing', 'Decreasing'),
            ('stable', 'Stable'),
        ],
        default='stable',
        help_text="Overall trend direction"
    )
    trend_strength = models.FloatField(
        default=0.0,
        help_text="Trend strength (0-1)"
    )

    # Peak periods
    peak_day_of_week = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), ],
        help_text="Peak day (0=Monday, 6=Sunday)"
    )
    peak_hour = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), ],
        help_text="Peak hour of day (0-23)"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-generated_at"]
        verbose_name = "Demand Forecast"
        verbose_name_plural = "Demand Forecasts"
        indexes = [
            models.Index(fields=["service", "-generated_at"]),
            models.Index(fields=["forecast_period", "-generated_at"]),
        ]

    def __str__(self):
        return f"{self.service.name} - {self.forecast_period.title()} ({self.forecast_start_date})"

    def get_forecast_values(self):
        """Parse forecast values from stored string."""
        if not self.forecast_values:
            return []
        try:
            return [float(x.strip()) for x in self.forecast_values.split(",")]
        except ValueError:
            return []

    def get_confidence_lower(self):
        """Parse lower confidence bounds."""
        if not self.confidence_lower:
            return []
        try:
            return [float(x.strip()) for x in self.confidence_lower.split(",")]
        except ValueError:
            return []

    def get_confidence_upper(self):
        """Parse upper confidence bounds."""
        if not self.confidence_upper:
            return []
        try:
            return [float(x.strip()) for x in self.confidence_upper.split(",")]
        except ValueError:
            return []


class ForecastMetric(models.Model):
    """Detailed metrics for forecast insights."""

    METRIC_TYPES = [
        ('peak_periods', 'Peak Periods'),
        ('low_periods', 'Low Periods'),
        ('seasonality_index', 'Seasonality Index'),
        ('volatility', 'Volatility'),
        ('growth_rate', 'Growth Rate'),
    ]

    forecast = models.ForeignKey(
        DemandForecast,
        on_delete=models.CASCADE,
        related_name='metrics',
        help_text="Associated forecast"
    )
    metric_type = models.CharField(
        max_length=50,
        choices=METRIC_TYPES,
        help_text="Type of metric"
    )
    label = models.CharField(
        max_length=255,
        help_text="Label for this metric"
    )
    value = models.FloatField(help_text="Metric value")
    insight = models.TextField(
        blank=True,
        help_text="Human-readable insight about this metric"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-value"]
        verbose_name = "Forecast Metric"
        verbose_name_plural = "Forecast Metrics"

    def __str__(self):
        return f"{self.label}: {self.value}"
