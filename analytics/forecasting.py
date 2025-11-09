"""
Business Intelligence and Forecasting Utilities
Uses Holt-Winters Exponential Smoothing for time series forecasting
"""
from datetime import timedelta
from typing import List, Dict, Any, Optional, Tuple
import math


class SimpleETS:
    """
    Simple implementation of Exponential Smoothing for forecasting.
    Falls back gracefully if statsmodels is not available.
    """

    @staticmethod
    def forecast_simple(data: List[float], periods: int = 7, alpha: float = 0.3) -> List[float]:
        """
        Simple exponential smoothing forecast.

        Args:
            data: Historical data points
            periods: Number of periods to forecast
            alpha: Smoothing parameter (0-1)

        Returns:
            List of forecasted values
        """
        if not data or len(data) < 2:
            # Not enough data, return average
            avg = sum(data) / len(data) if data else 0
            return [avg] * periods

        # Calculate simple exponential smoothing
        smoothed = [data[0]]
        for i in range(1, len(data)):
            smoothed.append(alpha * data[i] + (1 - alpha) * smoothed[i - 1])

        # Forecast
        last_value = smoothed[-1]
        return [last_value] * periods

    @staticmethod
    def forecast_trend(data: List[float], periods: int = 7, alpha: float = 0.3, beta: float = 0.1) -> List[float]:
        """
        Double exponential smoothing (Holt's method) with trend.

        Args:
            data: Historical data points
            periods: Number of periods to forecast
            alpha: Level smoothing parameter
            beta: Trend smoothing parameter

        Returns:
            List of forecasted values
        """
        if not data or len(data) < 3:
            return SimpleETS.forecast_simple(data, periods, alpha)

        # Initialize level and trend
        level = data[0]
        trend = (data[1] - data[0])

        forecasts = []

        # Update level and trend
        for value in data[1:]:
            last_level = level
            level = alpha * value + (1 - alpha) * (level + trend)
            trend = beta * (level - last_level) + (1 - beta) * trend

        # Generate forecasts
        for i in range(periods):
            forecast = level + (i + 1) * trend
            forecasts.append(max(0, forecast))  # Ensure non-negative

        return forecasts

    @staticmethod
    def forecast_seasonal(
        data: List[float],
        periods: int = 7,
        season_length: int = 7,
        alpha: float = 0.3,
        beta: float = 0.1,
        gamma: float = 0.1
    ) -> List[float]:
        """
        Triple exponential smoothing (Holt-Winters) with trend and seasonality.

        Args:
            data: Historical data points
            periods: Number of periods to forecast
            season_length: Length of seasonal cycle
            alpha: Level smoothing parameter
            beta: Trend smoothing parameter
            gamma: Seasonal smoothing parameter

        Returns:
            List of forecasted values
        """
        if not data or len(data) < season_length * 2:
            return SimpleETS.forecast_trend(data, periods, alpha, beta)

        # Initialize components
        level = sum(data[:season_length]) / season_length
        trend = 0

        # Initialize seasonal indices
        seasonal = []
        for i in range(season_length):
            seasonal.append(data[i] / level if level > 0 else 1)

        # Update components
        for i, value in enumerate(data):
            if value <= 0:
                continue

            old_level = level
            season_idx = i % season_length

            level = alpha * (value / seasonal[season_idx]) + (1 - alpha) * (level + trend)
            trend = beta * (level - old_level) + (1 - beta) * trend
            seasonal[season_idx] = gamma * (value / level) + (1 - gamma) * seasonal[season_idx]

        # Generate forecasts
        forecasts = []
        for i in range(periods):
            season_idx = (len(data) + i) % season_length
            forecast = (level + (i + 1) * trend) * seasonal[season_idx]
            forecasts.append(max(0, forecast))

        return forecasts


class BusinessIntelligence:
    """
    Business intelligence calculations and metrics.
    """

    @staticmethod
    def calculate_growth_rate(current: float, previous: float) -> float:
        """Calculate growth rate percentage."""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100

    @staticmethod
    def calculate_moving_average(data: List[float], window: int = 7) -> List[float]:
        """Calculate moving average."""
        if len(data) < window:
            return data

        ma = []
        for i in range(len(data)):
            if i < window - 1:
                ma.append(sum(data[:i + 1]) / (i + 1))
            else:
                ma.append(sum(data[i - window + 1:i + 1]) / window)
        return ma

    @staticmethod
    def detect_trend(data: List[float]) -> str:
        """
        Detect trend in data (increasing, decreasing, stable).
        """
        if not data or len(data) < 2:
            return "stable"

        # Calculate average slope
        n = len(data)
        x_mean = (n - 1) / 2
        y_mean = sum(data) / n

        numerator = sum((i - x_mean) * (data[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        # Classify trend
        if abs(slope) < 0.1:
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"

    @staticmethod
    def calculate_forecast_confidence(
        actual: List[float],
        forecast: List[float]
    ) -> Dict[str, float]:
        """
        Calculate forecast accuracy metrics.
        """
        if not actual or not forecast or len(actual) != len(forecast):
            return {"mae": 0, "mape": 0, "accuracy": 0}

        n = len(actual)

        # Mean Absolute Error
        mae = sum(abs(actual[i] - forecast[i]) for i in range(n)) / n

        # Mean Absolute Percentage Error
        mape_sum = 0
        count = 0
        for i in range(n):
            if actual[i] != 0:
                mape_sum += abs((actual[i] - forecast[i]) / actual[i])
                count += 1

        mape = (mape_sum / count * 100) if count > 0 else 0
        accuracy = max(0, 100 - mape)

        return {
            "mae": round(mae, 2),
            "mape": round(mape, 2),
            "accuracy": round(accuracy, 2)
        }

    @staticmethod
    def identify_peak_periods(data: List[Tuple[Any, float]], top_n: int = 5) -> List[Tuple[Any, float]]:
        """
        Identify peak periods from time series data.

        Args:
            data: List of (timestamp, value) tuples
            top_n: Number of top periods to return

        Returns:
            List of top periods sorted by value
        """
        if not data:
            return []

        sorted_data = sorted(data, key=lambda x: x[1], reverse=True)
        return sorted_data[:top_n]

    @staticmethod
    def calculate_seasonality_index(data: List[float], period_length: int = 7) -> List[float]:
        """
        Calculate seasonality indices for each period in the cycle.

        Args:
            data: Historical data
            period_length: Length of seasonal period (e.g., 7 for weekly)

        Returns:
            List of seasonality indices
        """
        if len(data) < period_length:
            return [1.0] * period_length

        # Group by period
        period_sums = [0.0] * period_length
        period_counts = [0] * period_length

        for i, value in enumerate(data):
            period_idx = i % period_length
            period_sums[period_idx] += value
            period_counts[period_idx] += 1

        # Calculate averages
        period_avgs = [
            period_sums[i] / period_counts[i] if period_counts[i] > 0 else 0
            for i in range(period_length)
        ]

        # Calculate overall average
        overall_avg = sum(period_avgs) / len([x for x in period_avgs if x > 0]) if any(period_avgs) else 1

        # Calculate indices
        indices = [
            (avg / overall_avg) if overall_avg > 0 else 1.0
            for avg in period_avgs
        ]

        return indices
