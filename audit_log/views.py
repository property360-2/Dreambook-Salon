"""Views for Audit Log Dashboard"""
from django.shortcuts import render
from django.views.generic import ListView, View
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import csv
import json

from core.mixins import StaffOrAdminRequiredMixin
from .models import AuditLog, AuditLogFilter
from core.models import User


class AuditLogDashboardView(StaffOrAdminRequiredMixin, ListView):
    """Main audit log dashboard with filtering and search"""
    model = AuditLog
    template_name = 'pages/audit_log_dashboard.html'
    context_object_name = 'audit_logs'
    paginate_by = 50

    def get_queryset(self):
        """Get filtered audit logs based on query parameters"""
        queryset = AuditLog.objects.select_related('user', 'content_type').all()

        # Filter by action type
        action_types = self.request.GET.getlist('action_types')
        if action_types:
            queryset = queryset.filter(action_type__in=action_types)

        # Filter by user
        user_id = self.request.GET.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by date range
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)

        date_to = self.request.GET.get('date_to')
        if date_to:
            date_to_end = timezone.datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            queryset = queryset.filter(timestamp__lte=date_to_end)

        # Search in description
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(user__email__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )

        return queryset.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_types'] = AuditLog.ACTION_TYPES
        context['users'] = User.objects.filter(is_active=True).order_by('email')
        context['saved_filters'] = AuditLogFilter.objects.filter(user=self.request.user)

        # Get current filters for display
        context['selected_action_types'] = self.request.GET.getlist('action_types')
        context['selected_user_id'] = self.request.GET.get('user_id', '')
        context['selected_date_from'] = self.request.GET.get('date_from', '')
        context['selected_date_to'] = self.request.GET.get('date_to', '')
        context['search_query'] = self.request.GET.get('search', '')

        return context


class AuditLogExportView(StaffOrAdminRequiredMixin, View):
    """Export audit logs to CSV"""

    def get(self, request):
        """Export filtered audit logs"""
        # Get same queryset as dashboard
        queryset = AuditLog.objects.select_related('user', 'content_type').all()

        # Apply same filters
        action_types = request.GET.getlist('action_types')
        if action_types:
            queryset = queryset.filter(action_type__in=action_types)

        user_id = request.GET.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        date_from = request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)

        date_to = request.GET.get('date_to')
        if date_to:
            date_to_end = timezone.datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            queryset = queryset.filter(timestamp__lte=date_to_end)

        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="audit_log_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Timestamp', 'User', 'Action', 'Target', 'IP Address', 'Description', 'Changes'])

        for log in queryset:
            writer.writerow([
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                log.user.email,
                log.get_action_type_display(),
                f"{log.content_type.name} #{log.object_id}" if log.content_type else "-",
                log.ip_address or "-",
                log.description,
                log.get_changes_display(),
            ])

        return response


class AuditLogStatsView(StaffOrAdminRequiredMixin, View):
    """Get audit log statistics as JSON (for dashboard stats)"""

    def get(self, request):
        """Return audit log statistics"""
        # Last 7 days of action counts by type
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_logs = AuditLog.objects.filter(timestamp__gte=seven_days_ago)

        action_counts = {}
        for action_type, _ in AuditLog.ACTION_TYPES:
            count = recent_logs.filter(action_type=action_type).count()
            action_counts[action_type] = count

        # Most active users (last 7 days)
        top_users = recent_logs.values('user__email').annotate(
            count=models.Count('id')
        ).order_by('-count')[:5]

        # Total logs
        total_logs = AuditLog.objects.count()

        return JsonResponse({
            'total_logs': total_logs,
            'logs_last_7_days': recent_logs.count(),
            'action_counts': action_counts,
            'top_users': list(top_users),
        })


# Import models for stats view
from django.db import models
