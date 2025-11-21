"""
Audit Logging Models for tracking critical business actions
"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from core.models import User
import json


class AuditLog(models.Model):
    """
    Records all critical actions in the system:
    - Appointment creation, status changes, cancellations
    - Payment creation and status changes
    - Inventory adjustments
    - User management actions
    """

    ACTION_TYPES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('STATUS_CHANGE', 'Status Changed'),
        ('PAYMENT_UPDATE', 'Payment Status Changed'),
        ('STOCK_ADJUSTMENT', 'Stock Adjusted'),
        ('APPOINTMENT_CANCEL', 'Appointment Cancelled'),
        ('USER_CREATE', 'User Created'),
        ('USER_UPDATE', 'User Updated'),
        ('USER_DELETE', 'User Deleted'),
        ('ROLE_CHANGE', 'Role Changed'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('USER_DEACTIVATE', 'User Deactivated'),
        ('USER_REACTIVATE', 'User Reactivated'),
        ('LOGIN', 'Logged In'),
        ('LOGOUT', 'Logged Out'),
    ]

    # Who performed the action
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='audit_actions')

    # What action
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES, db_index=True)

    # When
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Generic reference to any model (appointment, payment, user, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.CharField(max_length=50, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # What changed (JSON diff of before/after)
    changes = models.JSONField(default=dict, blank=True)

    # Additional context
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action_type', '-timestamp']),
            models.Index(fields=['content_type', 'object_id']),
        ]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        return f"{self.user.email} - {self.get_action_type_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    @classmethod
    def log_action(cls, user, action_type, description="", obj=None, changes=None, request=None):
        """
        Convenience method to log an action

        Args:
            user: User performing the action
            action_type: Type of action from ACTION_TYPES
            description: Human-readable description
            obj: Object being acted upon
            changes: Dict of changes (before/after values)
            request: HttpRequest object (for IP and user agent)
        """
        content_type = None
        object_id = None

        if obj:
            content_type = ContentType.objects.get_for_model(obj)
            object_id = str(obj.pk)

        ip_address = None
        user_agent = ""

        if request:
            ip_address = cls._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')

        return cls.objects.create(
            user=user,
            action_type=action_type,
            description=description,
            content_type=content_type,
            object_id=object_id,
            changes=changes or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')

    def get_changes_display(self):
        """Get formatted changes for display"""
        if not self.changes:
            return "No changes recorded"

        display = []
        for field, change in self.changes.items():
            if isinstance(change, dict) and 'before' in change and 'after' in change:
                display.append(f"{field}: {change['before']} → {change['after']}")
            else:
                display.append(f"{field}: {change}")

        return "; ".join(display)


class AuditLogFilter(models.Model):
    """
    Saved filters for audit log queries (allows users to save common searches)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_filters')
    name = models.CharField(max_length=200)

    # Filter criteria (stored as JSON)
    action_types = models.JSONField(default=list, blank=True)
    date_from = models.DateTimeField(null=True, blank=True)
    date_to = models.DateTimeField(null=True, blank=True)
    target_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audit_filters_as_target'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Audit Log Filters"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.name}"
