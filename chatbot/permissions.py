"""
Role-based access control for chatbot queries.
Validates whether a user has permission to execute specific intents and database queries.
"""
from typing import Tuple


class ChatbotPermissionValidator:
    """Validates chatbot query permissions based on user role."""

    # Define which intents require staff/admin access
    # Note: STAFF and ADMIN have identical access in chatbot
    STAFF_ONLY_INTENTS = [
        'revenue_inquiry',
        'inventory_inquiry',
        'appointment_analytics',
        'staff_list_inquiry',
        'all_appointments',
        'business_analytics'
    ]

    # Define which database queries require staff/admin access
    STAFF_ONLY_QUERIES = [
        'revenue_analytics',
        'appointment_analytics',
        'inventory_status',
        'staff_list',
        'all_appointments'
    ]

    @staticmethod
    def validate_intent_access(intent: str, user_role: str) -> Tuple[bool, str]:
        """
        Validate if user has permission to execute this intent.

        Args:
            intent: The detected intent
            user_role: 'ADMIN', 'STAFF', or 'CUSTOMER'

        Returns:
            Tuple of (is_allowed: bool, denial_message: str)
        """
        # Admin and Staff have access to everything
        if user_role in ['ADMIN', 'STAFF']:
            return True, ""

        # Check staff-only intents
        if intent in ChatbotPermissionValidator.STAFF_ONLY_INTENTS:
            return False, ChatbotPermissionValidator.get_access_denial_response(intent, user_role)

        # Customer intents are allowed for everyone
        return True, ""

    @staticmethod
    def validate_query_access(query_type: str, user_role: str) -> Tuple[bool, str]:
        """
        Validate if user has permission to execute this database query.

        Args:
            query_type: The database query type
            user_role: 'ADMIN', 'STAFF', or 'CUSTOMER'

        Returns:
            Tuple of (is_allowed: bool, denial_message: str)
        """
        # Admin and Staff have access to everything
        if user_role in ['ADMIN', 'STAFF']:
            return True, ""

        # Check staff-only queries
        if query_type in ChatbotPermissionValidator.STAFF_ONLY_QUERIES:
            return False, f"Sorry, only staff and administrators can access this information. Please contact management for assistance."

        # Customer queries are allowed for everyone
        return True, ""

    @staticmethod
    def get_access_denial_response(intent: str, user_role: str) -> str:
        """
        Generate a friendly access denial message.

        Args:
            intent: The intent that was denied
            user_role: The user's current role

        Returns:
            Formatted denial message
        """
        intent_descriptions = {
            'revenue_inquiry': 'revenue and financial information',
            'inventory_inquiry': 'inventory and stock information',
            'appointment_analytics': 'appointment analytics and statistics',
            'staff_list_inquiry': 'staff member information',
            'all_appointments': 'all customer appointments',
            'business_analytics': 'business analytics'
        }

        description = intent_descriptions.get(intent, 'this information')

        return f"Sorry, only staff and administrators can access {description}. Please contact management for assistance."
