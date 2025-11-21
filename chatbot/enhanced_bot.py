"""
Enhanced Intelligent Chatbot with Claude NLU and Context Management.
Bridges the original intelligent_bot with Claude API for better NLU.
"""
from .intelligent_bot import IntelligentChatbot
from .llm_integration import ClaudeNLU, LLMIntegrationError
from .fuzzy_matcher import FuzzyMatcher
from .models import ConversationHistory, ChatbotConfig
from services.models import Service
from datetime import datetime, timedelta
from django.db import models


class EnhancedChatbot:
    """
    Enhanced chatbot combining:
    1. Claude API for natural language understanding
    2. Existing intelligent_bot for database queries
    3. Fuzzy matching for typo tolerance
    4. Conversation history for context
    """

    def __init__(self, user=None, session_id=None):
        """
        Initialize the enhanced chatbot.

        Args:
            user: Django user object
            session_id: Session identifier for tracking conversations
        """
        self.user = user
        self.session_id = session_id or f"session_{datetime.now().timestamp()}"
        self.intelligent_bot = IntelligentChatbot(user=user)
        self.is_staff = user and user.is_authenticated and user.role in ['ADMIN', 'STAFF']

        # Try to initialize Claude NLU, fallback if not available
        try:
            self.nlu = ClaudeNLU()
            self.use_nlu = True
        except LLMIntegrationError as e:
            print(f"Claude NLU not available: {str(e)}")
            self.nlu = None
            self.use_nlu = False

        # Load chatbot configuration from database
        self.config = ChatbotConfig.objects.first()
        if not self.config:
            self.config = ChatbotConfig()

    def get_conversation_context(self, max_turns=5):
        """
        Retrieve recent conversation history for context.

        Args:
            max_turns: Maximum number of previous turns to retrieve

        Returns:
            list: Recent conversation turns
        """
        queryset = ConversationHistory.objects.filter(session_id=self.session_id).order_by('-created_at')[:max_turns]
        return [
            {
                'user_message': turn.user_message,
                'bot_response': turn.bot_response,
                'intent_detected': turn.intent_detected,
                'created_at': turn.created_at
            }
            for turn in reversed(queryset)
        ]

    def process_message(self, user_message, save_to_history=True):
        """
        Process user message and return intelligent response.

        Main flow:
        1. If Claude NLU available: Use Claude for NLU, then database queries
        2. Otherwise: Use original intelligent bot (regex-based) as fallback
        3. Save conversation to history

        Args:
            user_message: User's message
            save_to_history: Whether to save to conversation history

        Returns:
            dict: {
                "response": "bot response",
                "intent": "detected intent",
                "confidence": 0.0-1.0,
                "error": None or error message
            }
        """
        try:
            # If Claude NLU not available, use original intelligent bot
            if not self.use_nlu:
                response = self.intelligent_bot.process_message(user_message)
                if save_to_history:
                    self._save_to_history(user_message, response, "regex_bot", 0.8)
                return {
                    "response": response,
                    "intent": "processed",
                    "confidence": 0.8,
                    "error": None
                }

            # Get conversation context
            context = self.get_conversation_context()

            # Step 1: Claude detects intent and extracts entities
            intent_result = self.nlu.detect_intent(
                user_message,
                user_role="staff" if self.is_staff else "customer",
                conversation_context=context
            )

            intent = intent_result.get("intent", "invalid")
            confidence = intent_result.get("confidence", 0.0)
            entities = intent_result.get("entities", {})
            requires_db_query = intent_result.get("requires_db_query", False)

            # Step 2: Check for clarification needed
            if intent_result.get("clarification_needed"):
                response = intent_result.get("clarification_needed")
                self._save_to_history(user_message, response, intent, confidence)
                return {
                    "response": response,
                    "intent": intent,
                    "confidence": confidence,
                    "error": None
                }

            # Step 3: Query database if needed
            db_data = {}
            if requires_db_query:
                db_data = self._query_database_by_intent(
                    intent_result.get("query_type"),
                    entities
                )

            # Step 4: Generate natural response using Claude
            response = self.nlu.generate_response(
                user_message,
                db_data=db_data,
                context=context,
                user_role="staff" if self.is_staff else "customer"
            )

            # Step 5: Save to conversation history
            if save_to_history:
                self._save_to_history(user_message, response, intent, confidence)

            return {
                "response": response,
                "intent": intent,
                "confidence": confidence,
                "error": None
            }

        except LLMIntegrationError as e:
            # Fallback to regex-based bot if Claude API fails
            response = self.intelligent_bot.process_message(user_message)
            if save_to_history:
                self._save_to_history(user_message, response, "fallback", 0.8)
            return {
                "response": response,
                "intent": "fallback",
                "confidence": 0.8,
                "error": None
            }
        except Exception as e:
            print(f"EnhancedChatbot error: {str(e)}")
            # Always fallback to regex bot on any error
            try:
                response = self.intelligent_bot.process_message(user_message)
                if save_to_history:
                    self._save_to_history(user_message, response, "error_fallback", 0.7)
                return {
                    "response": response,
                    "intent": "error_fallback",
                    "confidence": 0.7,
                    "error": None
                }
            except:
                response = "I'm sorry, I'm having trouble processing your request. Please try again."
                if save_to_history:
                    self._save_to_history(user_message, response, "critical_error", 0.0)
                return {
                    "response": response,
                    "intent": "critical_error",
                    "confidence": 0.0,
                    "error": None
                }

    def _query_database_by_intent(self, query_type, entities):
        """
        Query database based on detected intent.

        Args:
            query_type: Type of query to perform
            entities: Extracted entities from user message

        Returns:
            dict: Relevant database data
        """
        try:
            if query_type == "list_services":
                services = Service.objects.filter(is_active=True).values(
                    'name', 'price', 'duration_minutes', 'description'
                )
                return {"services": list(services)}

            elif query_type == "get_pricing":
                service_name = entities.get("service_name")
                if service_name:
                    # Fuzzy match service
                    service_names = list(Service.objects.filter(is_active=True).values_list('name', flat=True))
                    matched_name, _ = FuzzyMatcher.find_best_match(service_name, service_names)
                    if matched_name:
                        service = Service.objects.get(name=matched_name)
                        return {
                            "service": {
                                "name": service.name,
                                "price": float(service.price),
                                "duration": service.duration_minutes,
                                "requires_downpayment": service.requires_downpayment,
                                "downpayment_amount": float(service.downpayment_amount) if service.requires_downpayment else 0
                            }
                        }
                return {"all_services": list(Service.objects.filter(is_active=True).values('name', 'price'))}

            elif query_type == "check_availability":
                date_str = entities.get("date")
                if date_str:
                    # Simple availability check
                    return self.intelligent_bot.check_date_availability(date_str)

            elif query_type == "get_popular_services":
                return self.intelligent_bot.get_popular_services()

            elif query_type == "revenue_analytics" and self.is_staff:
                return self.intelligent_bot.get_revenue_analytics()

            elif query_type == "appointment_stats" and self.is_staff:
                return self.intelligent_bot.get_appointment_stats()

            elif query_type == "top_services" and self.is_staff:
                return self.intelligent_bot.get_top_services_analytics()

            return {}

        except Exception as e:
            return {"error": f"Database query failed: {str(e)}"}

    def _save_to_history(self, user_message, bot_response, intent, confidence):
        """
        Save conversation turn to database history.

        Args:
            user_message: User's message
            bot_response: Bot's response
            intent: Detected intent
            confidence: Confidence score
        """
        try:
            ConversationHistory.objects.create(
                user=self.user,
                session_id=self.session_id,
                user_message=user_message,
                bot_response=bot_response,
                intent_detected=intent,
                confidence_score=confidence
            )
        except Exception as e:
            # Log but don't fail if history saving fails
            print(f"Failed to save conversation history: {str(e)}")

    def get_chatbot_config(self):
        """Get chatbot configuration (business hours, location, etc.)"""
        return {
            "business_hours": self.config.business_hours,
            "location": self.config.location,
            "contact_phone": self.config.contact_phone,
            "contact_email": self.config.contact_email,
            "max_daily_appointments": self.config.max_daily_appointments
        }

    def get_conversation_stats(self):
        """Get statistics for this conversation session."""
        history = ConversationHistory.objects.filter(session_id=self.session_id)
        total_turns = history.count()
        avg_confidence = history.aggregate(
            models.Avg('confidence_score')
        )['confidence_score__avg'] or 0.0

        return {
            "total_turns": total_turns,
            "average_confidence": round(avg_confidence, 2),
            "session_id": self.session_id,
            "user": self.user.email if self.user else "Anonymous"
        }
