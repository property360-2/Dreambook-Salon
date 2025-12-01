from django.urls import path
from .views import (
    ReportDashboardView,
    RevenueReportView,
    ServicePerformanceView,
    GenerateReportAPIView,
    ExportReportAPIView,
)

app_name = 'reports'

urlpatterns = [
    # Report pages
    path('', ReportDashboardView.as_view(), name='dashboard'),
    path('revenue/', RevenueReportView.as_view(), name='revenue'),
    path('service-performance/', ServicePerformanceView.as_view(), name='service_performance'),

    # API endpoints
    path('api/generate/', GenerateReportAPIView.as_view(), name='api_generate'),
    path('api/export/<int:report_id>/', ExportReportAPIView.as_view(), name='api_export'),
]
