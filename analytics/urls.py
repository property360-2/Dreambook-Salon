from django.urls import path
from .views import (
    AnalyticsDashboardView,
    RevenueChartView,
    ServiceAnalyticsView,
    InventoryAnalyticsView,
)

app_name = 'analytics'

urlpatterns = [
    path('', AnalyticsDashboardView.as_view(), name='dashboard'),
    path('revenue/', RevenueChartView.as_view(), name='revenue'),
    path('services/', ServiceAnalyticsView.as_view(), name='services'),
    path('inventory/', InventoryAnalyticsView.as_view(), name='inventory'),
]
