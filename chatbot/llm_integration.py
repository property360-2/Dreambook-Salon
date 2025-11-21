"""
LLM Integration - Uses Claude API for natural language understanding
while preserving the existing database query system.
"""
import anthropic
import json
import os
from datetime import datetime


class LLMIntegrationError(Exception):
    """Custom exception for LLM integration errors."""
    pass


class ClaudeNLU:
    """
    Claude-powered Natural Language Understanding for the chatbot.
    Handles:
    - Intent detection with high accuracy
    - Entity extraction (service names, dates, etc.)
    - Context understanding across multi-turn conversations
    - User sentiment and request clarity
    """

    def __init__(self):
        """Initialize Claude API client."""
        # Check if API key is configured
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise LLMIntegrationError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Claude NLU is unavailable. Using fallback mode."
            )

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.available = True

    def detect_intent(self, user_message, user_role="customer", conversation_context=None):
        """
        Detect user intent using Claude NLU.

        Args:
            user_message: The user's message
            user_role: Either 'customer' or 'staff'
            conversation_context: Previous conversation turns for context

        Returns:
            dict: {
                "intent": "service_inquiry" | "booking" | "payment" | etc.,
                "confidence": 0.0-1.0,
                "entities": {
                    "service_name": str | None,
                    "date": str | None,
                    "time": str | None,
                    "quantity": int | None,
                    ...
                },
                "requires_db_query": bool,
                "query_type": str | None,  # e.g., "list_services", "check_availability"
                "clarification_needed": str | None,  # If unclear what user wants
            }
        """
        context_text = ""
        if conversation_context:
            context_text = "\n".join([
                f"User: {turn['user_message']}\nBot: {turn['bot_response']}"
                for turn in conversation_context[-3:]  # Last 3 turns for context
            ])
            context_text = f"Previous conversation:\n{context_text}\n\n"

        role_context = f"User role: {user_role}\n\n"
        if user_role == "staff":
            role_context += "This user is staff/admin and can request analytics and business intelligence.\n\n"

        prompt = f"""{role_context}{context_text}Current user message: "{user_message}"

Analyze this message and respond with ONLY valid JSON (no markdown, no extra text). The JSON must follow this exact structure:

{{
  "intent": "one of: greeting, service_inquiry, pricing, booking, payment, availability_check, order_status, complaint, feedback, staff_analytics, staff_reporting, general_help, invalid",
  "confidence": 0.75,
  "entities": {{
    "service_name": null or "name of the service if mentioned",
    "date": null or "date if mentioned (any format)",
    "time": null or "time if mentioned",
    "quantity": null or number,
    "customer_name": null or "name if mentioned",
    "other_relevant": null or "any other extracted info"
  }},
  "requires_db_query": true or false,
  "query_type": null or "one of: list_services, get_pricing, check_availability, get_popular_services, booking_inquiry, payment_status, revenue_analytics, appointment_stats, customer_insights, inventory_status, top_services",
  "clarification_needed": null or "question to ask user if their intent is unclear",
  "sentiment": "positive, neutral, or negative",
  "is_polite": true or false,
  "requires_human_followup": true or false
}}

Requirements:
- Be strict about intent classification
- Extract ALL relevant entities from the message
- Only set requires_db_query to true if a database lookup is actually needed
- If message is unclear or could mean multiple things, set clarification_needed
- For pricing/availability, always set requires_db_query to true
- Always respond with ONLY valid JSON, nothing else
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse the JSON response
            response_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            response_text = response_text.strip()

            intent_data = json.loads(response_text)
            return intent_data

        except json.JSONDecodeError as e:
            raise LLMIntegrationError(f"Failed to parse Claude response as JSON: {str(e)}")
        except anthropic.APIError as e:
            raise LLMIntegrationError(f"Claude API error: {str(e)}")

    def generate_response(self, user_message, db_data=None, context=None, user_role="customer"):
        """
        Generate a natural, conversational response using Claude.

        Args:
            user_message: The user's original message
            db_data: Data from database queries (dict with relevant info)
            context: Conversation history context
            user_role: Either 'customer' or 'staff'

        Returns:
            str: Natural language response
        """
        context_text = ""
        if context:
            context_text = "Conversation history:\n"
            for turn in context[-2:]:  # Last 2 turns
                context_text += f"Customer: {turn['user_message']}\n"
                context_text += f"Assistant: {turn['bot_response']}\n"
            context_text += "\n"

        db_context = ""
        if db_data:
            db_context = f"\nDatabase information retrieved:\n{json.dumps(db_data, indent=2, default=str)}\n"

        system_prompt = f"""You are a helpful chatbot assistant for Dreambook Salon, a beauty and wellness service provider.
Your role is to help customers book appointments, answer questions about services, and assist with payments.
You are knowledgeable, friendly, and always professional.

User role: {user_role}
{"You have access to staff analytics and business intelligence data." if user_role == "staff" else ""}

Always:
- Be concise but helpful (2-4 sentences typically)
- Use emoji sparingly for visual interest
- Provide clear, actionable information
- If information is incomplete or you need clarification, ask follow-up questions
- Format lists with bullets when appropriate
- Include relevant details from the database information provided

Never:
- Make up information not provided in database results
- Promise specific dates without checking availability
- Discuss pricing without confirming with current data
- Make guarantees about availability"""

        user_prompt = f"""{context_text}User message: "{user_message}"{db_context}
Respond naturally and helpfully to this message."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )

            return response.content[0].text

        except anthropic.APIError as e:
            return f"I apologize, but I'm having trouble processing your request. Please try again. (Error: {str(e)})"

    def extract_service_name(self, message, available_services):
        """
        Use Claude to intelligently extract service name from message.
        More accurate than regex-based matching.

        Args:
            message: User message
            available_services: List of available service names

        Returns:
            tuple: (service_name, confidence) or (None, 0.0)
        """
        prompt = f"""User message: "{message}"

Available services: {', '.join(available_services)}

Identify which service the user is asking about. Respond with ONLY valid JSON:
{{
  "service_name": "service name if found or null",
  "confidence": 0.0,
  "reason": "brief explanation"
}}

If none match or the user isn't asking about a specific service, set service_name to null."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            response_text = response.content[0].text.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            response_text = response_text.strip()

            data = json.loads(response_text)
            return data.get("service_name"), data.get("confidence", 0.0)

        except Exception as e:
            return None, 0.0
