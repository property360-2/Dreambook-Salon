from django.db import models


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
