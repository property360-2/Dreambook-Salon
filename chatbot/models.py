from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatbotConfig(models.Model):
    """Configuration model for chatbot settings."""

    business_hours = models.CharField(
        max_length=200,
        default="Monday-Friday: 10:00 AM - 8:00 PM, Saturday: 10:00 AM - 6:00 PM, Sunday: Closed",
        help_text="Business operating hours"
    )
    location = models.CharField(
        max_length=500,
        default="Dreambook Salon, Manila, Philippines",
        help_text="Business location/address"
    )
    contact_phone = models.CharField(
        max_length=20,
        default="+63 2 1234 5678",
        help_text="Business phone number"
    )
    contact_email = models.EmailField(
        default="info@dreambook.com",
        help_text="Business email address"
    )
    max_daily_appointments = models.IntegerField(
        default=10,
        help_text="Maximum concurrent appointments per time slot"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chatbot Configuration"
        verbose_name_plural = "Chatbot Configuration"

    def __str__(self):
        return "Chatbot Settings"


class ConversationHistory(models.Model):
    """Model to store chatbot conversation history for context."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chatbot_conversations",
        null=True,
        blank=True,
        help_text="User having the conversation (null for anonymous)"
    )
    session_id = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Session identifier for tracking conversation"
    )
    user_message = models.TextField(
        help_text="Message from the user"
    )
    bot_response = models.TextField(
        help_text="Response from the chatbot"
    )
    intent_detected = models.CharField(
        max_length=100,
        blank=True,
        help_text="Detected intent/category of the message"
    )
    confidence_score = models.FloatField(
        default=0.0,
        help_text="Confidence score of intent detection (0-1)"
    )
    was_helpful = models.BooleanField(
        null=True,
        blank=True,
        help_text="User feedback on whether response was helpful"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Conversation History"
        verbose_name_plural = "Conversation Histories"
        indexes = [
            models.Index(fields=["session_id", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        user_info = f"{self.user.email}" if self.user else "Anonymous"
        return f"{user_info}: {self.user_message[:50]}..."


class Rule(models.Model):
    """Chatbot rule model for keyword-based responses."""

    keyword = models.CharField(
        max_length=200,
        db_index=True,
        help_text="Keyword to match (case-insensitive)",
    )
    response = models.TextField(help_text="Bot response when keyword matches")
    is_active = models.BooleanField(
        default=True, help_text="Whether this rule is active"
    )
    priority = models.IntegerField(
        default=0,
        help_text="Higher priority rules match first (useful for specific vs general keywords)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "keyword"]
        verbose_name = "Chatbot Rule"
        verbose_name_plural = "Chatbot Rules"

    def __str__(self):
        status = "✓" if self.is_active else "✗"
        return f"{status} {self.keyword} → {self.response[:50]}..."

    def matches(self, message):
        """Check if this rule matches the given message."""
        return self.keyword.lower() in message.lower()
