"""URL configuration for Audit Log"""
from django.urls import path
from . import views

app_name = 'audit_log'

urlpatterns = [
    path('dashboard/', views.AuditLogDashboardView.as_view(), name='dashboard'),
    path('export/', views.AuditLogExportView.as_view(), name='export'),
    path('stats/', views.AuditLogStatsView.as_view(), name='stats'),
]
