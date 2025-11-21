from django.contrib import admin

from .models import Rule, ChatbotConfig, ConversationHistory


@admin.register(ChatbotConfig)
class ChatbotConfigAdmin(admin.ModelAdmin):
    list_display = ("__str__", "location", "contact_phone", "updated_at")
    readonly_fields = ("updated_at",)

    fieldsets = (
        ("Business Information", {
            "fields": ("location", "contact_phone", "contact_email", "business_hours")
        }),
        ("Configuration", {
            "fields": ("max_daily_appointments",)
        }),
        ("Timestamps", {
            "fields": ("updated_at",)
        }),
    )

    def has_add_permission(self, request):
        """Prevent adding multiple config instances."""
        return not ChatbotConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deleting config."""
        return False


@admin.register(ConversationHistory)
class ConversationHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "session_id", "intent_detected", "confidence_score", "created_at")
    list_filter = ("intent_detected", "confidence_score", "created_at")
    search_fields = ("user__email", "session_id", "user_message", "intent_detected")
    readonly_fields = ("created_at", "user_message_display", "bot_response_display")
    date_hierarchy = "created_at"

    fieldsets = (
        ("Conversation", {
            "fields": ("user", "session_id", "user_message_display", "bot_response_display")
        }),
        ("Analysis", {
            "fields": ("intent_detected", "confidence_score", "was_helpful")
        }),
        ("Timestamp", {
            "fields": ("created_at",)
        }),
    )

    def user_message_display(self, obj):
        """Display user message with word wrapping."""
        return obj.user_message
    user_message_display.short_description = "User Message"

    def bot_response_display(self, obj):
        """Display bot response with word wrapping."""
        return obj.bot_response
    bot_response_display.short_description = "Bot Response"

    def has_add_permission(self, request):
        """Prevent manual addition of conversation history."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion for cleanup."""
        return True


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ("keyword", "is_active", "priority", "response_preview", "created_at")
    list_filter = ("is_active", "priority", "created_at")
    search_fields = ("keyword", "response")
    readonly_fields = ("created_at", "updated_at")
    list_editable = ("is_active", "priority")

    def response_preview(self, obj):
        """Show preview of response."""
        return obj.response[:50] + "..." if len(obj.response) > 50 else obj.response

    response_preview.short_description = "Response Preview"
