from django.urls import path
from django.views.generic import TemplateView
from .views import (
    AnalyticsDashboardView,
    RevenueChartView,
    ServiceAnalyticsView,
    InventoryAnalyticsView,
    BusinessIntelligenceView,
    WeeklySeasonalChartDataView,
    MonthlyServiceDemandChartDataView,
    RevenueVsCancellationsChartDataView,
    StylistUtilizationChartDataView,
)

app_name = 'analytics'

urlpatterns = [
    path('', AnalyticsDashboardView.as_view(), name='dashboard'),
    path('revenue/', RevenueChartView.as_view(), name='revenue'),
    path('services/', ServiceAnalyticsView.as_view(), name='services'),
    path('inventory/', InventoryAnalyticsView.as_view(), name='inventory'),
    path('business-intelligence/', BusinessIntelligenceView.as_view(), name='business_intelligence'),
    path('charts/', TemplateView.as_view(template_name='pages/analytics_charts.html'), name='charts'),

    # Chart.js API endpoints
    path('api/weekly-seasonal/', WeeklySeasonalChartDataView.as_view(), name='api_weekly_seasonal'),
    path('api/monthly-service-demand/', MonthlyServiceDemandChartDataView.as_view(), name='api_monthly_demand'),
    path('api/revenue-cancellations/', RevenueVsCancellationsChartDataView.as_view(), name='api_revenue_cancellations'),
    path('api/stylist-utilization/', StylistUtilizationChartDataView.as_view(), name='api_stylist_utilization'),
]
