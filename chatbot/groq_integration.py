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

        self.client = Groq(api_key=api_key)
        self.model = "mixtral-8x7b-32768"  # Fast and capable model
        self.available = True

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

Analyze this message and respond with ONLY valid JSON (no markdown):
{{
  "intent": "greeting|service_inquiry|pricing|booking|payment|availability_check|order_status|complaint|feedback|staff_analytics|general_help|invalid",
  "confidence": 0.85,
  "entities": {{
    "service_name": null or "extracted service name",
    "date": null or "extracted date",
    "time": null or "extracted time",
    "customer_name": null or "customer name if mentioned"
  }},
  "requires_db_query": true or false,
  "query_type": null or "list_services|get_pricing|check_availability|appointment_status|popular_services",
  "sentiment": "positive|neutral|negative",
  "clarity": "clear|needs_clarification"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )

            response_text = response.content[0].text.strip()
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

        system_prompt = """You are an intelligent, friendly chatbot assistant for Dreambook Salon.
You help customers book appointments, answer service questions, and handle inquiries professionally.

Personality:
- Friendly and conversational
- Professional and knowledgeable
- Use emojis sparingly (✨, 📅, 💅, etc.)
- Concise but helpful (2-4 sentences usually)

When given database information:
- Use it to provide specific, accurate details
- Never make up information
- Always reference what you find in the data
- Suggest actions based on availability

Response Rules:
- Be clear and actionable
- Ask clarifying questions if needed
- Format lists with bullets
- Always professional but warm"""

        try:
            response = self.client.messages.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{context_text}User message: \"{user_message}\"{db_context}\n\nRespond naturally and helpfully."}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.content[0].text

        except Exception as e:
            return f"I apologize, but I'm having difficulty processing your request. Please try again or contact our support team."

    def process_with_tools(self, user_message: str, available_tools: Dict[str, callable], context: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Process message with tool/function calling capabilities.

        Args:
            user_message: User message
            available_tools: Dict of tool_name -> callable
            context: Conversation history

        Returns:
            Dict with response and any tool calls made
        """
        intent_data = self.detect_intent(user_message, conversation_context=context)

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
