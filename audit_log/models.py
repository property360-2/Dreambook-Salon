"""
Audit Logging Models for tracking critical business actions
"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from core.models import User


class AuditLog(models.Model):
    """
    Records all critical actions in the system:
    - Appointment creation, status changes, cancellations
    - Payment creation and status changes
    - Inventory adjustments
    - User management actions
    """

    SOURCE_TYPES = [
        ('APPLICATION', 'Application Code'),
        ('MIDDLEWARE', 'Middleware'),
        ('SYSTEM', 'System'),
    ]

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
    actor_email = models.EmailField(max_length=254, blank=True, null=True)
    actor_name = models.CharField(max_length=255, blank=True, null=True)
    actor_role = models.CharField(max_length=50, blank=True, null=True)

    # Where this log originated
    source = models.CharField(max_length=20, choices=SOURCE_TYPES, db_index=True, blank=True, null=True)

    # What action
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES, db_index=True)

    # When
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Generic reference to any model (appointment, payment, user, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.CharField(max_length=50, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Target snapshot
    target_type = models.CharField(max_length=100, blank=True, null=True)
    target_repr = models.CharField(max_length=255, blank=True, null=True)

    # Request context
    request_method = models.CharField(max_length=10, blank=True, null=True)
    request_path = models.CharField(max_length=500, blank=True, null=True)
    route_name = models.CharField(max_length=200, blank=True, null=True)
    status_code = models.PositiveIntegerField(null=True, blank=True)

    # What changed (JSON diff of before/after)
    changes = models.JSONField(default=dict, blank=True)

    # Additional context
    metadata = models.JSONField(blank=True, null=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action_type', '-timestamp']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['source', '-timestamp']),
        ]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        actor = self.actor_email or getattr(self.user, 'email', 'Unknown')
        action = self.get_action_type_display()
        target = self.target_repr
        if not target and self.content_type:
            target = f"{self.content_type} #{self.object_id}"
        return f"{actor} - {action} - {target or 'N/A'} @ {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    @classmethod
    def log_action(cls, user, action_type, description="", obj=None, changes=None, request=None,
                   status_code=None, source="APPLICATION", metadata=None):
        """
        Convenience method to log an action

        Args:
            user: User performing the action
            action_type: Type of action from ACTION_TYPES
            description: Human-readable description
            obj: Object being acted upon
            changes: Dict of changes (before/after values)
            request: HttpRequest object (for IP and user agent)
            status_code: Optional HTTP status code for the action
            source: Origin of the log (application code vs middleware)
            metadata: Additional structured context to store with the log
        """
        content_type = None
        object_id = None
        target_type = None
        target_repr = None

        if obj:
            content_type = ContentType.objects.get_for_model(obj)
            object_id = str(getattr(obj, 'pk', ''))
            target_type = content_type.model_class().__name__ if content_type else obj.__class__.__name__
            target_repr = cls._get_target_repr(obj)

        ip_address = None
        user_agent = ""
        request_method = None
        request_path = None
        route_name = None

        if request:
            ip_address = cls._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            request_method = getattr(request, 'method', None)
            request_path = getattr(request, 'path', None)
            resolver_match = getattr(request, 'resolver_match', None)
            route_name = resolver_match.view_name if resolver_match else None

        actor_name, actor_role = cls._get_actor_details(user)
        actor_email = getattr(user, 'email', None) if user else None

        normalized_changes = cls._normalize_changes(changes)
        metadata_payload = dict(metadata or {})
        request_id = None
        if request:
            request_id = request.META.get('HTTP_X_REQUEST_ID') or request.META.get('HTTP_X_CORRELATION_ID')
        if request_id and 'request_id' not in metadata_payload:
            metadata_payload['request_id'] = request_id

        if not description:
            description = cls._build_default_description(action_type, target_repr, request_path)

        return cls.objects.create(
            user=user,
            action_type=action_type,
            description=description,
            content_type=content_type,
            object_id=object_id,
            target_type=target_type,
            target_repr=target_repr,
            changes=normalized_changes,
            ip_address=ip_address,
            user_agent=user_agent,
            actor_email=actor_email,
            actor_name=actor_name,
            actor_role=actor_role,
            source=source,
            request_method=request_method,
            request_path=request_path,
            route_name=route_name,
            status_code=status_code,
            metadata=metadata_payload or {},
        )

    @staticmethod
    def _build_default_description(action_type, target_repr=None, request_path=None):
        """Create a predictable fallback description when none is provided."""
        action_label = dict(AuditLog.ACTION_TYPES).get(action_type, action_type.replace('_', ' ').title())
        if target_repr:
            return f"{action_label} {target_repr}"
        if request_path:
            return f"{action_label} at {request_path}"
        return action_label

    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')

    @staticmethod
    def _get_target_repr(obj):
        """Generate a human-readable target representation"""
        for attr in ('name', 'title', 'email'):
            if hasattr(obj, attr):
                value = getattr(obj, attr)
                if value:
                    return str(value)
        return str(obj)

    @staticmethod
    def _get_actor_details(user):
        """Snapshot actor details to preserve history even if the user changes later"""
        if not user:
            return None, None

        name = ""
        if hasattr(user, "get_full_name"):
            name = user.get_full_name() or ""
        if not name:
            first = getattr(user, "first_name", "") or ""
            last = getattr(user, "last_name", "") or ""
            name = f"{first} {last}".strip()

        return name or None, getattr(user, "role", None)

    @classmethod
    def _normalize_changes(cls, changes):
        """Ensure changes are stored in a consistent before/after format"""
        if not changes:
            return {}

        normalized = {}
        for field, change in changes.items():
            if isinstance(change, dict) and 'before' in change and 'after' in change:
                normalized[field] = {
                    'before': cls._stringify_value(change.get('before')),
                    'after': cls._stringify_value(change.get('after')),
                }
            else:
                normalized[field] = {
                    'before': None,
                    'after': cls._stringify_value(change),
                }
        return normalized

    @staticmethod
    def _stringify_value(value):
        """Convert values to JSON-serializable strings without losing important context"""
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return value
        return str(value)

    def get_changes_display(self):
        """Get formatted changes for display"""
        if not self.changes:
            return "No changes recorded"

        display = []
        for field, change in self.changes.items():
            if isinstance(change, dict) and 'before' in change and 'after' in change:
                display.append(f"{field}: {change['before']} -> {change['after']}")
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
