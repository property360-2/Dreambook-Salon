"""
Intelligent Chatbot Service
Combines GROQ LLM + Database queries for comprehensive chatbot functionality
"""
from typing import Dict, Optional, List, Any
import uuid
from django.utils import timezone

from .groq_integration import GroqChatbot
from .db_queries import ChatbotDBQueries
from .models import ConversationHistory


class IntelligentChatbotService:
    """
    Complete intelligent chatbot service combining:
    - GROQ LLM for ultra-fast responses
    - Database queries for real-time data
    - Conversation history tracking
    - Multi-turn context understanding
    """

    def __init__(self, user=None, session_id: Optional[str] = None):
        """Initialize the service."""
        try:
            self.groq = GroqChatbot()
        except Exception as e:
            print(f"Warning: GROQ not available - {str(e)}")
            self.groq = None

        self.user = user
        self.session_id = session_id or str(uuid.uuid4())

        # Enhanced role detection
        if user and hasattr(user, 'role'):
            self.user_role = user.role  # 'ADMIN', 'STAFF', or 'CUSTOMER'
        else:
            self.user_role = 'CUSTOMER'  # Default for anonymous users

        # Backward compatibility
        self.is_staff = self.user_role in ['ADMIN', 'STAFF']
        self.is_admin = self.user_role == 'ADMIN'

        # Initialize role-aware tools
        self.db_tools = ChatbotDBQueries.get_tools_dict(user_role=self.user_role)

    def get_conversation_context(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation history for context."""
        try:
            history = ConversationHistory.objects.filter(
                session_id=self.session_id
            ).order_by('-created_at')[:limit]

            return [
                {
                    'user_message': h.user_message,
                    'bot_response': h.bot_response,
                    'intent': h.intent_detected,
                }
                for h in reversed(history)
            ]
        except Exception:
            return []

    def process_message(self, user_message: str, save_history: bool = True) -> Dict[str, Any]:
        """
        Process user message with full intelligence and role-based access control.

        Returns:
            {
                'response': str,
                'intent': str,
                'confidence': float,
                'tools_used': List[str],
                'error': Optional[str],
                'access_denied': bool
            }
        """
        try:
            if not self.groq:
                return {
                    'response': "I'm sorry, but the AI service is currently unavailable. Please contact support.",
                    'intent': 'error',
                    'confidence': 0.0,
                    'tools_used': [],
                    'error': 'GROQ not initialized',
                    'access_denied': False
                }

            # Get conversation context
            context = self.get_conversation_context(limit=4)

            # Get intent from GROQ with role information
            from .permissions import ChatbotPermissionValidator

            # First detect intent
            intent_result = self.groq.detect_intent(
                user_message=user_message,
                user_role=self.user_role,
                conversation_context=context
            )

            # Validate access permissions
            intent = intent_result.get('intent', 'unknown')
            is_allowed, denial_message = ChatbotPermissionValidator.validate_intent_access(
                intent=intent,
                user_role=self.user_role
            )

            if not is_allowed:
                # Access denied - return friendly denial message
                if save_history:
                    try:
                        ConversationHistory.objects.create(
                            user=self.user,
                            session_id=self.session_id,
                            user_message=user_message,
                            bot_response=denial_message,
                            intent_detected=f"{intent}_denied",
                            confidence_score=1.0,
                        )
                    except Exception as e:
                        print(f"Failed to save conversation history: {str(e)}")

                return {
                    'response': denial_message,
                    'intent': intent,
                    'confidence': intent_result.get('confidence', 0.0),
                    'tools_used': [],
                    'error': None,
                    'access_denied': True
                }

            # Process with GROQ and database tools (access is allowed)
            # Add user_id to entities for appointment queries
            result = self.groq.process_with_tools(
                user_message=user_message,
                available_tools=self.db_tools,
                context=context,
                user_role=self.user_role
            )

            # Inject user_id into entities if user is authenticated
            if self.user and 'entities' in result:
                if 'user_id' not in result['entities']:
                    result['entities']['user_id'] = self.user.id

            # Check if any tool returned permission denied
            if result.get('tool_results'):
                for tool_name, tool_data in result['tool_results'].items():
                    if isinstance(tool_data, dict) and tool_data.get('error') == 'Permission denied':
                        # Override response with denial message
                        result['response'] = tool_data.get('message',
                            'Sorry, you do not have permission to access this information.')
                        result['access_denied'] = True
                        break

            # Enhance response for staff/admin on analytics queries
            if self.user_role in ['ADMIN', 'STAFF'] and result['intent'] in ['revenue_inquiry', 'appointment_analytics', 'inventory_inquiry']:
                result['response'] = self._enhance_staff_response(result)

            # Save to conversation history
            if save_history:
                try:
                    ConversationHistory.objects.create(
                        user=self.user,
                        session_id=self.session_id,
                        user_message=user_message,
                        bot_response=result['response'],
                        intent_detected=result.get('intent', ''),
                        confidence_score=result.get('confidence', 0.0),
                    )
                except Exception as e:
                    print(f"Failed to save conversation history: {str(e)}")

            return {
                'response': result['response'],
                'intent': result.get('intent', 'unknown'),
                'confidence': result.get('confidence', 0.0),
                'tools_used': result.get('tools_used', []),
                'error': None,
                'access_denied': result.get('access_denied', False)
            }

        except Exception as e:
            error_msg = str(e)
            return {
                'response': f"I encountered an error processing your request: {error_msg}",
                'intent': 'error',
                'confidence': 0.0,
                'tools_used': [],
                'error': error_msg,
                'access_denied': False
            }

    def _enhance_staff_response(self, result: Dict) -> str:
        """Add staff-specific insights to response."""
        if result.get('tool_results'):
            # Add analytics formatting for staff
            tools_data = result['tool_results']

            # If revenue or appointment analytics were queried, add summary
            if 'revenue_analytics' in tools_data:
                revenue_data = tools_data['revenue_analytics']
                if 'total_revenue' in revenue_data:
                    result['response'] += f"\n\n💰 **Revenue Summary**: ₱{revenue_data['total_revenue']} in last {revenue_data['period_days']} days"

            if 'appointment_analytics' in tools_data:
                appt_data = tools_data['appointment_analytics']
                if 'total' in appt_data:
                    result['response'] += f"\n📊 **Appointment Stats**: {appt_data['total']} total, {appt_data['completed']} completed, {appt_data['completion_rate']} rate"

        return result['response']

    def handle_service_inquiry(self, service_name: str) -> str:
        """Handle specific service inquiry."""
        service_data = ChatbotDBQueries.get_service_by_name(service_name)

        if not service_data.get('found'):
            return f"I couldn't find '{service_name}'. Would you like me to show you our available services?"

        # Format service information
        response = f"""✨ **{service_data['name']}**

💰 Price: ₱{service_data['price']}
⏱️ Duration: {service_data['duration']}
📝 {service_data['description']}"""

        if service_data.get('features'):
            response += f"\n✓ Includes: {', '.join(service_data['features'])}"

        if service_data.get('requires_downpayment'):
            response += f"\n💳 Down payment required: ₱{service_data['downpayment_amount']}"

        response += "\n\nWould you like to book this service? 📅"

        return response

    def handle_booking_inquiry(self, service_name: str, date_str: Optional[str] = None) -> str:
        """Handle booking inquiry."""
        service_data = ChatbotDBQueries.get_service_by_name(service_name)

        if not service_data.get('found'):
            return f"I couldn't find the service '{service_name}'. Please specify a valid service name."

        if not date_str:
            return f"Great! To book {service_data['name']}, please provide your preferred date and time. 📅"

        # Check availability
        avail_data = ChatbotDBQueries.check_availability(
            service_id=service_data['id'],
            date_str=date_str,
            time_str="10:00"  # Default time if not specified
        )

        if avail_data['available']:
            return f"""Perfect! {service_data['name']} is available on {date_str}! ✅

To complete your booking, please visit: /appointments/book/?service={service_data['id']}

Ready to secure your appointment? 💅"""
        else:
            return f"""I'm sorry, that time slot is not available for {service_data['name']}.

{avail_data.get('message', 'Please try another date or time.')}

Would you like to check availability for a different date? 📅"""

    def get_quick_help(self) -> str:
        """Provide quick help message."""
        return """👋 Hello! I'm your Dreambook Salon assistant. I can help you with:

✨ **Browse Services** - "Show me your services" or "What services do you offer?"
💰 **Check Pricing** - "How much does [service] cost?"
📅 **Book Appointments** - "I want to book [service]"
⏱️ **Check Availability** - "Is [service] available on [date]?"
📱 **Business Hours** - "When are you open?"
📊 **View My Appointments** - "Show my bookings"

What can I help you with today? 😊"""


# Fallback function for when GROQ is not available
def get_fallback_response(intent: str, message: str) -> str:
    """Provide fallback responses when LLM is unavailable."""
    fallback_responses = {
        'greeting': "Hello! 👋 Welcome to Dreambook Salon. How can I help you today?",
        'service_inquiry': "We offer a variety of beauty and wellness services. Would you like to see our full list?",
        'pricing': "Our services range from ₱500 to ₱5,000. What service interests you?",
        'booking': "I'd love to help you book an appointment! Which service would you like?",
        'availability_check': "To check availability, please let me know the service and preferred date.",
        'general_help': "I'm here to help with appointments, services, pricing, and more! What do you need?",
    }

    return fallback_responses.get(intent, "I'm not sure how to help with that. Could you clarify your question?")
