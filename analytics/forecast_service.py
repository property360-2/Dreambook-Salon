"""
Demand Forecasting Service
Uses historical booking data and exponential smoothing to predict future demand
"""
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any
from django.utils import timezone
from django.db.models import Count
from appointments.models import Appointment
from services.models import Service
from .models import DemandForecast, ForecastMetric
from .forecasting import SimpleETS, BusinessIntelligence


class DemandForecastingService:
    """Service for generating and managing demand forecasts."""

    @staticmethod
    def get_historical_daily_data(service: Service, days: int = 90) -> List[Tuple[str, int]]:
        """
        Get historical daily booking counts for a service.

        Args:
            service: Service instance
            days: Number of days of history to retrieve

        Returns:
            List of (date, count) tuples
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        data = Appointment.objects.filter(
            service=service,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status__in=[Appointment.Status.COMPLETED, Appointment.Status.CONFIRMED]
        ).values('created_at__date').annotate(
            count=Count('id')
        ).order_by('created_at__date')

        return [(str(item['created_at__date']), item['count']) for item in data]

    @staticmethod
    def get_historical_weekly_data(service: Service, weeks: int = 12) -> List[Tuple[int, int]]:
        """
        Get historical weekly booking counts for a service.

        Args:
            service: Service instance
            weeks: Number of weeks of history to retrieve

        Returns:
            List of (week_number, count) tuples
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(weeks=weeks)

        data = Appointment.objects.filter(
            service=service,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status__in=[Appointment.Status.COMPLETED, Appointment.Status.CONFIRMED]
        ).values('created_at__week').annotate(
            count=Count('id')
        ).order_by('created_at__week')

        return [(item['created_at__week'], item['count']) for item in data]

    @staticmethod
    def forecast_daily_demand(
        service: Service,
        periods: int = 7,
        historical_days: int = 90,
        method: str = "seasonal"
    ) -> DemandForecast:
        """
        Generate daily demand forecast for a service.

        Args:
            service: Service to forecast
            periods: Number of days to forecast
            historical_days: Number of historical days to use
            method: Forecasting method (simple, trend, seasonal)

        Returns:
            DemandForecast instance
        """
        # Get historical data
        historical_data = DemandForecastingService.get_historical_daily_data(service, historical_days)
        booking_counts = [count for _, count in historical_data]

        # Pad with zeros if needed
        if len(booking_counts) < 7:
            booking_counts = [0] * (7 - len(booking_counts)) + booking_counts

        # Generate forecast
        if method == "simple":
            forecasts = SimpleETS.forecast_simple(booking_counts, periods)
        elif method == "trend":
            forecasts = SimpleETS.forecast_trend(booking_counts, periods)
        else:  # seasonal
            forecasts = SimpleETS.forecast_seasonal(booking_counts, periods, season_length=7)

        # Calculate confidence bounds (±20% of forecast)
        confidence_lower = [max(0, f * 0.8) for f in forecasts]
        confidence_upper = [f * 1.2 for f in forecasts]

        # Calculate metrics
        trend = BusinessIntelligence.detect_trend(booking_counts)
        moving_avg = BusinessIntelligence.calculate_moving_average(booking_counts, window=7)
        seasonality = BusinessIntelligence.calculate_seasonality_index(booking_counts, period_length=7)

        # Calculate trend strength
        trend_strength = 0.0
        if len(moving_avg) > 1:
            diffs = [moving_avg[i+1] - moving_avg[i] for i in range(len(moving_avg)-1)]
            avg_diff = sum(diffs) / len(diffs) if diffs else 0
            max_val = max(moving_avg) if moving_avg else 1
            trend_strength = min(1.0, abs(avg_diff) / max(max_val, 1))

        # Identify peak day
        peak_day = 0
        if seasonality:
            peak_day = seasonality.index(max(seasonality))

        # Create forecast
        end_date = timezone.now().date()
        start_date = end_date + timedelta(days=1)
        end_forecast_date = start_date + timedelta(days=periods-1)

        forecast = DemandForecast.objects.create(
            service=service,
            forecast_type=method,
            forecast_period=DemandForecast.ForecastPeriod.DAILY,
            forecast_start_date=start_date,
            forecast_end_date=end_forecast_date,
            periods_ahead=periods,
            forecast_values=",".join(str(int(f)) for f in forecasts),
            confidence_lower=",".join(str(f) for f in confidence_lower),
            confidence_upper=",".join(str(f) for f in confidence_upper),
            accuracy_mae=0.0,  # Will be calculated when actual data arrives
            accuracy_mape=0.0,
            accuracy_score=85.0,  # Default confidence score
            trend_direction=trend,
            trend_strength=trend_strength,
            peak_day_of_week=peak_day,
        )

        # Create metric records
        for i, (day_idx, season_idx) in enumerate([(i % 7, i % 7) for i in range(periods)]):
            ForecastMetric.objects.create(
                forecast=forecast,
                metric_type='seasonality_index',
                label=f"Day {i+1} ({['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][day_idx]})",
                value=seasonality[season_idx] if season_idx < len(seasonality) else 1.0,
                insight=f"Forecasted demand: {int(forecasts[i])} bookings"
            )

        return forecast

    @staticmethod
    def forecast_weekly_demand(
        service: Service,
        periods: int = 4,
        historical_weeks: int = 12,
        method: str = "seasonal"
    ) -> DemandForecast:
        """
        Generate weekly demand forecast for a service.

        Args:
            service: Service to forecast
            periods: Number of weeks to forecast
            historical_weeks: Number of historical weeks to use
            method: Forecasting method (simple, trend, seasonal)

        Returns:
            DemandForecast instance
        """
        # Get historical data
        historical_data = DemandForecastingService.get_historical_weekly_data(service, historical_weeks)
        booking_counts = [count for _, count in historical_data]

        if len(booking_counts) < 4:
            booking_counts = [0] * (4 - len(booking_counts)) + booking_counts

        # Generate forecast
        if method == "simple":
            forecasts = SimpleETS.forecast_simple(booking_counts, periods)
        elif method == "trend":
            forecasts = SimpleETS.forecast_trend(booking_counts, periods)
        else:
            forecasts = SimpleETS.forecast_seasonal(booking_counts, periods, season_length=4)

        # Calculate confidence bounds
        confidence_lower = [max(0, f * 0.8) for f in forecasts]
        confidence_upper = [f * 1.2 for f in forecasts]

        # Calculate metrics
        trend = BusinessIntelligence.detect_trend(booking_counts)
        trend_strength = 0.5

        # Create forecast
        end_date = timezone.now().date()
        # Get next Monday
        days_until_monday = (7 - end_date.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        start_date = end_date + timedelta(days=days_until_monday)
        end_forecast_date = start_date + timedelta(weeks=periods-1)

        forecast = DemandForecast.objects.create(
            service=service,
            forecast_type=method,
            forecast_period=DemandForecast.ForecastPeriod.WEEKLY,
            forecast_start_date=start_date,
            forecast_end_date=end_forecast_date,
            periods_ahead=periods,
            forecast_values=",".join(str(int(f)) for f in forecasts),
            confidence_lower=",".join(str(f) for f in confidence_lower),
            confidence_upper=",".join(str(f) for f in confidence_upper),
            accuracy_mae=0.0,
            accuracy_mape=0.0,
            accuracy_score=85.0,
            trend_direction=trend,
            trend_strength=trend_strength,
        )

        return forecast

    @staticmethod
    def get_all_service_forecasts(period: str = "daily") -> Dict[str, Any]:
        """
        Get forecasts for all active services.

        Args:
            period: Forecast period (daily, weekly, monthly)

        Returns:
            Dictionary with service forecasts
        """
        services = Service.objects.filter(is_archived=False, is_active=True)
        forecasts = {}

        for service in services:
            try:
                # Get latest forecast for this service and period
                forecast = DemandForecast.objects.filter(
                    service=service,
                    forecast_period=period
                ).latest('generated_at')

                forecasts[service.id] = {
                    'service': service,
                    'forecast': forecast,
                    'values': forecast.get_forecast_values(),
                    'lower': forecast.get_confidence_lower(),
                    'upper': forecast.get_confidence_upper(),
                }
            except DemandForecast.DoesNotExist:
                forecasts[service.id] = {
                    'service': service,
                    'forecast': None,
                    'values': [],
                    'lower': [],
                    'upper': [],
                }

        return forecasts

    @staticmethod
    def generate_all_forecasts() -> Dict[str, int]:
        """
        Generate forecasts for all active services.

        Returns:
            Summary of generated forecasts
        """
        services = Service.objects.filter(is_archived=False, is_active=True)
        results = {
            'daily': 0,
            'weekly': 0,
            'errors': 0,
        }

        for service in services:
            try:
                DemandForecastingService.forecast_daily_demand(service, periods=7)
                results['daily'] += 1
            except Exception as e:
                results['errors'] += 1
                print(f"Error forecasting {service.name} (daily): {str(e)}")

            try:
                DemandForecastingService.forecast_weekly_demand(service, periods=4)
                results['weekly'] += 1
            except Exception as e:
                results['errors'] += 1
                print(f"Error forecasting {service.name} (weekly): {str(e)}")

        return results
