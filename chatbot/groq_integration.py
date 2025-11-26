"""
GROQ Integration - Ultra-fast LLM for intelligent chatbot responses
Uses GROQ API for real-time conversational AI with database query support
"""
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List


class GroqIntegrationError(Exception):
    """Custom exception for GROQ integration errors."""
    pass


class GroqChatbot:
    """
    GROQ-powered intelligent chatbot for Dreambook Salon.
    Features:
    - Ultra-fast inference with Mistral/Llama models
    - Database query integration for real-time data
    - Multi-turn conversation understanding
    - Intent detection and entity extraction
    - Context-aware responses
    """

    def __init__(self):
        """Initialize GROQ client."""
        try:
            from groq import Groq
        except ImportError:
            raise GroqIntegrationError(
                "groq package not installed. Install it with: pip install groq"
            )

        api_key = os.environ.get('GROQ_API_KEY')
        if not api_key:
            raise GroqIntegrationError(
                "GROQ_API_KEY environment variable not set"
            )

        # Fix for Render deployment: Remove proxy env vars that cause initialization errors
        # Save current proxy settings
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'NO_PROXY', 'no_proxy']
        saved_proxies = {}
        for var in proxy_vars:
            if var in os.environ:
                saved_proxies[var] = os.environ.pop(var)

        try:
            # Initialize Groq client without proxy interference
            self.client = Groq(api_key=api_key)
            self.model = "llama-3.1-8b-instant"  # Fast and capable model (updated from deprecated mixtral)
            self.available = True
        finally:
            # Restore proxy settings if needed by other services
            for var, value in saved_proxies.items():
                os.environ[var] = value

    def detect_intent(self, user_message: str, user_role: str = "customer", conversation_context: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Detect user intent using GROQ NLU.

        Args:
            user_message: The user's message
            user_role: Either 'customer' or 'staff'
            conversation_context: Previous conversation turns

        Returns:
            dict with intent, confidence, entities, and database query needs
        """
        context_text = ""
        if conversation_context:
            context_text = "\n".join([
                f"User: {turn['user_message']}\nBot: {turn['bot_response']}"
                for turn in conversation_context[-3:]
            ])
            context_text = f"Previous conversation:\n{context_text}\n\n"

        prompt = f"""{context_text}User message: "{user_message}"
User role: {user_role}

Analyze this message and respond with ONLY valid JSON (no markdown):
{{
  "intent": "greeting|service_inquiry|pricing|booking|payment|availability_check|my_appointments|complaint|feedback|revenue_inquiry|inventory_inquiry|appointment_analytics|staff_list_inquiry|all_appointments|business_analytics|general_help|invalid",
  "confidence": 0.85,
  "entities": {{
    "service_name": null or "extracted service name (hair, massage, facial, nails, spa, etc.)",
    "date": null or "extracted date",
    "time": null or "extracted time",
    "customer_name": null or "customer name if mentioned",
    "days": null or number of days for analytics (7, 30, 90)
  }},
  "requires_db_query": true or false,
  "query_type": null or "list_services|get_pricing|check_availability|popular_services|business_hours|my_appointments|revenue_analytics|appointment_analytics|inventory_status|staff_list|all_appointments",
  "requires_staff_access": false or true,
  "sentiment": "positive|neutral|negative",
  "clarity": "clear|needs_clarification"
}}

CRITICAL INTENT CLASSIFICATION RULES:
CUSTOMER intents (accessible to all):
- Service/pricing questions → "service_inquiry" or "pricing", query_type="list_services" or "get_pricing"
- Availability check → "availability_check", query_type="check_availability"
- User's own appointments → "my_appointments", query_type="my_appointments"
- Popular services → query_type="popular_services"
- Business hours → query_type="business_hours"

STAFF-ONLY intents (requires_staff_access=true):
- Revenue questions ("how much money", "total sales", "revenue", "income") → "revenue_inquiry", query_type="revenue_analytics", requires_staff_access=true
- Inventory ("stock", "inventory", "supplies") → "inventory_inquiry", query_type="inventory_status", requires_staff_access=true
- Appointment statistics ("how many appointments", "completion rate", "analytics") → "appointment_analytics", query_type="appointment_analytics", requires_staff_access=true
- Staff information ("who are the staff", "employees", "staff list") → "staff_list_inquiry", query_type="staff_list", requires_staff_access=true
- All customer appointments (not "my appointments") → "all_appointments", query_type="all_appointments", requires_staff_access=true

Extract days for analytics queries (default to 30 if not specified).
Extract service names like: hair, hairstyle, haircut, massage, facial, nails, spa, etc."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )

            response_text = response.choices[0].message.content.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            response_text = response_text.strip()

            return json.loads(response_text)

        except json.JSONDecodeError:
            return {
                "intent": "invalid",
                "confidence": 0.0,
                "entities": {},
                "requires_db_query": False,
                "sentiment": "neutral",
                "clarity": "needs_clarification"
            }
        except Exception as e:
            raise GroqIntegrationError(f"GROQ API error: {str(e)}")

    def generate_response(self, user_message: str, db_data: Optional[Dict] = None, context: Optional[List[Dict]] = None, user_role: str = "customer") -> str:
        """
        Generate intelligent response using GROQ with database context.

        Args:
            user_message: User's message
            db_data: Data from database queries
            context: Conversation history
            user_role: customer or staff

        Returns:
            Natural language response
        """
        context_text = ""
        if context:
            context_text = "Recent conversation:\n"
            for turn in context[-2:]:
                context_text += f"Customer: {turn['user_message']}\n"
                context_text += f"Assistant: {turn['bot_response']}\n"
            context_text += "\n"

        db_context = ""
        if db_data:
            db_context = f"\n📊 Available Data:\n{json.dumps(db_data, indent=2, default=str)}\n"

        system_prompt = """You are a helpful chatbot assistant for Dreambook Salon, a Filipino salon business.

CRITICAL RULES:
1. NEVER make up prices, services, or information
2. ONLY use data provided in the database information below
3. ALL prices MUST use Philippine Peso symbol (₱) - NEVER use $ or other currencies
4. If no database information is provided, say you need to check and ask them to contact the salon
5. Be natural and conversational - avoid sounding robotic or overly formal

Personality:
- Friendly and helpful (like talking to a real salon staff)
- Professional but warm
- Use emojis occasionally (✨, 📅, 💅) but don't overdo it
- Keep responses concise (2-4 sentences)

When database information IS provided:
- Use ONLY the exact prices and service names from the data
- Format all amounts with ₱ symbol (e.g., ₱500, ₱1,200)
- List actual services available, not generic ones
- Be specific and accurate

When NO database information provided:
- Politely say you need to check the current details
- Suggest they visit the salon or call for specifics
- Do NOT make up any services or prices"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{context_text}User message: \"{user_message}\"{db_context}\n\nRespond naturally and helpfully."}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"I apologize, but I'm having difficulty processing your request. Please try again or contact our support team."

    def process_with_tools(self, user_message: str, available_tools: Dict[str, callable], context: Optional[List[Dict]] = None, user_role: str = 'CUSTOMER') -> Dict[str, Any]:
        """
        Process message with tool/function calling capabilities.

        Args:
            user_message: User message
            available_tools: Dict of tool_name -> callable
            context: Conversation history
            user_role: User's role for access control

        Returns:
            Dict with response and any tool calls made
        """
        intent_data = self.detect_intent(user_message, user_role=user_role, conversation_context=context)

        tools_to_use = []
        if intent_data.get('requires_db_query') and intent_data.get('query_type'):
            query_type = intent_data['query_type']
            if query_type in available_tools:
                tools_to_use.append(query_type)

        tool_results = {}
        for tool_name in tools_to_use:
            try:
                tool_results[tool_name] = available_tools[tool_name](intent_data.get('entities', {}))
            except Exception as e:
                tool_results[tool_name] = {"error": str(e)}

        # Generate response with tool results
        response = self.generate_response(
            user_message,
            db_data=tool_results if tool_results else None,
            context=context
        )

        return {
            "response": response,
            "intent": intent_data.get('intent'),
            "confidence": intent_data.get('confidence', 0.0),
            "tools_used": tools_to_use,
            "tool_results": tool_results,
            "entities": intent_data.get('entities', {})
        }
