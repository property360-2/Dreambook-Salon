from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    """User notification model for in-app messages."""

    NOTIFICATION_TYPES = [
        ('booking_confirmed', 'Booking Confirmed'),
        ('booking_reminder', 'Booking Reminder'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('payment_received', 'Payment Received'),
        ('payment_failed', 'Payment Failed'),
        ('service_update', 'Service Update'),
        ('system_message', 'System Message'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        default='system_message'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.URLField(blank=True, null=True, help_text="Link to related resource")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.title} ({self.user.email})"

    @classmethod
    def create_notification(cls, user, notification_type, title, message, link=None):
        """Create a notification for a user."""
        return cls.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link
        )

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
        return self

    def mark_as_unread(self):
        """Mark notification as unread."""
        if self.is_read:
            self.is_read = False
            self.save(update_fields=['is_read'])
        return self
