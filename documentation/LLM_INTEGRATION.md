# LLM Integration: Claude AI Chatbot Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Claude API Integration](#claude-api-integration)
4. [Intent Detection](#intent-detection)
5. [Response Generation](#response-generation)
6. [Fallback System](#fallback-system)
7. [Conversation Management](#conversation-management)
8. [Error Handling](#error-handling)
9. [Code Examples](#code-examples)
10. [API Reference](#api-reference)

---

## Overview

The Dreambook Salon chatbot integrates **Anthropic's Claude API** (specifically Claude 3.5 Sonnet) with a comprehensive fallback system to provide intelligent, context-aware customer service. The system automatically falls back to a regex-based intelligent bot when the Claude API is unavailable.

### Key Characteristics
- **Model**: Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
- **Response Time**: Typically 500-1500ms per request
- **Token Limit**: Up to 200,000 input tokens per request
- **Max Output**: 4,096 output tokens per response
- **Multi-Turn**: Maintains conversation history for context
- **Cost**: $3/1M input tokens, $15/1M output tokens

### System Components
```
┌─────────────────────────────────────────────────┐
│         User Input (Chatbot Interface)          │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────▼─────────────┐
        │  EnhancedChatbot Class   │ ← Orchestrator
        │  (enhanced_bot.py)       │
        └────────────┬─────────────┘
                     │
        ┌────────────▼──────────────────┐
        │ Claude NLU Available?          │
        │ (Check API Key)                │
        └────────┬──────────────┬────────┘
                 │              │
            YES  │              │  NO
                 │              │
    ┌────────────▼──┐  ┌────────▼──────────┐
    │ Claude API    │  │ IntelligentChatbot│
    │ (NLU + Gen)   │  │ (Regex-based)     │
    └────────────┬──┘  └────────┬──────────┘
                 │              │
                 └────────┬──────┘
                          │
                ┌─────────▼────────┐
                │ ConversationDB   │
                │ (History Saving) │
                └──────────────────┘
```

---

## Architecture

### Component Overview

#### 1. **ClaudeNLU** (`llm_integration.py`)
Handles all Claude API interactions:
- Intent detection and classification
- Entity extraction (service names, dates, times)
- Response generation with context
- Error handling and API management

#### 2. **EnhancedChatbot** (`enhanced_bot.py`)
Orchestrates the full bot system:
- Initializes Claude NLU (with fallback)
- Manages conversation context
- Bridges database queries with AI responses
- Maintains conversation history

#### 3. **IntelligentChatbot** (`intelligent_bot.py`)
Regex-based fallback system:
- 107+ intent patterns
- Database query handlers
- Specific query handlers (price, duration, availability)
- Staff analytics queries

#### 4. **Fuzzy Matcher** (`fuzzy_matcher.py`)
Typo tolerance for service names:
- Levenshtein distance calculation
- Approximate string matching
- Service name normalization

#### 5. **Response Enhancer** (`response_enhancer.py`)
Input validation and response formatting:
- Date validation
- Service name verification
- Confidence scoring
- Source attribution

---

## Claude API Integration

### API Configuration

```python
# llm_integration.py
import anthropic
import os

class ClaudeNLU:
    def __init__(self):
        # Initialize API client
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise LLMIntegrationError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Claude NLU is unavailable. Using fallback mode."
            )

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.available = True
```

### Environment Setup

```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-your-secret-key-here
```

### API Key Acquisition

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create account or sign in
3. Navigate to "API Keys"
4. Generate new API key
5. Copy and store securely in `.env`

---

## Intent Detection

### Purpose
Classifies user input into predefined intent categories and extracts relevant entities.

### Intent Categories
```
- greeting              → Hello, hi, good morning
- service_inquiry       → What services do you have?
- pricing               → How much is the haircut?
- booking               → I want to book an appointment
- payment               → How do I pay?
- availability_check    → Do you have slots on 12/26?
- order_status          → What's my appointment status?
- complaint             → Poor service experience
- feedback              → Great service!
- staff_analytics       → Revenue, appointments, inventory
- staff_reporting       → Business intelligence queries
- general_help          → General questions
- invalid               → Unrecognizable input
```

### Intent Detection Process

```python
def detect_intent(self, user_message, user_role="customer", conversation_context=None):
    """
    Detect user intent using Claude NLU.

    Returns:
    {
        "intent": "service_inquiry",
        "confidence": 0.95,
        "entities": {
            "service_name": "hair spa",
            "date": null,
            "time": null,
            "quantity": null
        },
        "requires_db_query": true,
        "query_type": "list_services",
        "clarification_needed": null,
        "sentiment": "neutral",
        "is_polite": true,
        "requires_human_followup": false
    }
    """

    # Build context from previous conversations
    context_text = ""
    if conversation_context:
        context_text = "\n".join([
            f"User: {turn['user_message']}\nBot: {turn['bot_response']}"
            for turn in conversation_context[-3:]  # Last 3 turns
        ])

    # Build prompt for Claude
    prompt = f"""User role: {user_role}
{context_text if context_text else ""}

Current user message: "{user_message}"

Analyze this message and respond with ONLY valid JSON..."""

    # Call Claude API
    response = self.client.messages.create(
        model=self.model,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse and return JSON response
    response_text = response.content[0].text.strip()
    intent_data = json.loads(response_text)
    return intent_data
```

### Response Format

```json
{
  "intent": "pricing",
  "confidence": 0.92,
  "entities": {
    "service_name": "hair spa",
    "date": null,
    "time": null,
    "quantity": null
  },
  "requires_db_query": true,
  "query_type": "get_pricing",
  "clarification_needed": null,
  "sentiment": "neutral",
  "is_polite": true,
  "requires_human_followup": false
}
```

### Entity Extraction

Entities are key information extracted from user input:

| Entity | Example | Used For |
|--------|---------|----------|
| service_name | "hair spa", "haircut" | Service lookup |
| date | "12/26/2025", "tomorrow" | Availability checking |
| time | "2:00 PM", "14:00" | Slot availability |
| quantity | "3" people | Batch bookings |
| customer_name | "John Doe" | Personalization |
| other_relevant | Payment method, etc. | Context |

---

## Response Generation

### Purpose
Generates natural, contextually appropriate responses based on:
- User input
- Retrieved database information
- Conversation history
- User role (customer vs staff)

### Response Generation Process

```python
def generate_response(self, user_message, db_data=None, context=None, user_role="customer"):
    """
    Generate natural language response using Claude.

    Args:
        user_message: Original user message
        db_data: Data retrieved from database
        context: Conversation history (last 2 turns)
        user_role: "customer" or "staff"

    Returns:
        str: Natural language response
    """

    # Build conversation context
    context_text = ""
    if context:
        context_text = "Conversation history:\n"
        for turn in context[-2:]:  # Last 2 turns only
            context_text += f"Customer: {turn['user_message']}\n"
            context_text += f"Assistant: {turn['bot_response']}\n"

    # Build database context
    db_context = ""
    if db_data:
        db_context = f"\nDatabase information:\n{json.dumps(db_data, indent=2)}\n"

    # System prompt (role-specific)
    system_prompt = f"""You are a helpful chatbot for Dreambook Salon.
Your role is to help customers book appointments and answer questions.
User role: {user_role}

{("You have access to staff analytics." if user_role == "staff" else "")}

Always:
- Be concise (2-4 sentences typically)
- Use emoji sparingly
- Provide clear, actionable information
- Ask follow-up questions if needed
- Format lists with bullets

Never:
- Make up information
- Promise specific dates without checking
- Discuss pricing without confirming
- Make availability guarantees"""

    # Generate response
    response = self.client.messages.create(
        model=self.model,
        max_tokens=500,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": f"{context_text}User message: \"{user_message}\"{db_context}\nRespond naturally."
        }]
    )

    return response.content[0].text
```

### Response Quality Guidelines

1. **Conciseness**: 2-4 sentences for most queries
2. **Accuracy**: Only use provided data, don't hallucinate
3. **Politeness**: Always maintain professional tone
4. **Clarity**: Use simple, clear language
5. **Actionability**: Provide specific next steps
6. **Emoji Usage**: Minimal and purposeful

---

## Fallback System

### Three-Layer Fallback

```
┌──────────────────────────────────────────┐
│ Layer 1: Claude API (Primary)            │
│ - Intent detection with NLU              │
│ - Context-aware responses                │
│ - Entity extraction                      │
│ - High confidence (0.85+)                │
└────────────────┬─────────────────────────┘
                 │ (API unavailable or error)
┌────────────────▼─────────────────────────┐
│ Layer 2: IntelligentChatbot (Fallback)   │
│ - 107+ regex patterns                    │
│ - Database query handlers                │
│ - Specific intent matching               │
│ - Confidence: 0.8                        │
└────────────────┬─────────────────────────┘
                 │ (IntelligentBot fails)
┌────────────────▼─────────────────────────┐
│ Layer 3: Generic Error Message           │
│ - "I'm sorry, I'm having trouble..."     │
│ - Confidence: 0.0                        │
│ - Suggests user contact support          │
└──────────────────────────────────────────┘
```

### Fallback Implementation

```python
# enhanced_bot.py
class EnhancedChatbot:
    def __init__(self, user=None, session_id=None):
        self.user = user
        self.session_id = session_id
        self.intelligent_bot = IntelligentChatbot(user=user)

        # Try Claude NLU, set flag if unavailable
        try:
            self.nlu = ClaudeNLU()
            self.use_nlu = True
        except LLMIntegrationError as e:
            print(f"Claude NLU not available: {str(e)}")
            self.nlu = None
            self.use_nlu = False

    def process_message(self, user_message, save_to_history=True):
        try:
            # If Claude not available, use regex-based bot
            if not self.use_nlu:
                response = self.intelligent_bot.process_message(user_message)
                self._save_to_history(user_message, response, "regex_bot", 0.8)
                return {
                    "response": response,
                    "intent": "processed",
                    "confidence": 0.8,
                    "error": None
                }

            # Step 1: Claude detects intent
            context = self.get_conversation_context()
            intent_result = self.nlu.detect_intent(
                user_message,
                user_role="staff" if self.is_staff else "customer",
                conversation_context=context
            )

            # Step 2-4: Process with database queries, generate response
            intent = intent_result.get("intent", "invalid")
            confidence = intent_result.get("confidence", 0.0)

            # ... rest of processing

        except LLMIntegrationError as e:
            # Fallback to regex bot if Claude fails
            response = self.intelligent_bot.process_message(user_message)
            self._save_to_history(user_message, response, "fallback", 0.8)
            return {
                "response": response,
                "intent": "fallback",
                "confidence": 0.8,
                "error": None
            }
        except Exception as e:
            # Ultimate fallback
            try:
                response = self.intelligent_bot.process_message(user_message)
                return {"response": response, ...}
            except:
                return {
                    "response": "I'm sorry, I'm having trouble processing...",
                    "intent": "critical_error",
                    "confidence": 0.0,
                    "error": None
                }
```

### When Fallback Triggers

1. **API Key Missing**: `ANTHROPIC_API_KEY` not set
2. **API Error**: Network/connection issues
3. **Rate Limiting**: Too many requests
4. **Timeout**: Response takes > 30 seconds
5. **Invalid Response**: JSON parsing error

---

## Conversation Management

### Conversation History

The system maintains conversation history in the database for:
- **Context Awareness**: Using previous turns for better understanding
- **User Satisfaction**: Tracking helpful/unhelpful responses
- **Analytics**: Identifying common issues
- **Improvement**: Training data for bot refinement

### Storage Schema

```python
# chatbot/models.py
class ConversationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100)
    user_message = models.TextField()
    bot_response = models.TextField()
    intent_detected = models.CharField(max_length=50)
    confidence_score = models.FloatField()
    was_helpful = models.NullBooleanField()  # User feedback
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['session_id', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
```

### Context Retrieval

```python
def get_conversation_context(self, max_turns=5):
    """
    Retrieve recent conversation for context.

    Returns last N conversation turns in chronological order.
    """
    queryset = ConversationHistory.objects.filter(
        session_id=self.session_id
    ).order_by('-created_at')[:max_turns]

    return [
        {
            'user_message': turn.user_message,
            'bot_response': turn.bot_response,
            'intent_detected': turn.intent_detected,
            'created_at': turn.created_at
        }
        for turn in reversed(queryset)
    ]
```

### Multi-Turn Conversation Example

```
Turn 1:
  User: "What's your most popular service?"
  Intent: service_inquiry
  Bot: "Our most popular service is Hair Spa..."

Turn 2:
  User: "How much does it cost?"
  Intent: pricing (with context from Turn 1)
  Bot: "Hair Spa costs ₱500 for 75 minutes..."

Turn 3:
  User: "Can I book it for tomorrow?"
  Intent: booking (with context from Turns 1-2)
  Bot: "Let me check availability for tomorrow..."
```

---

## Error Handling

### Error Types & Responses

| Error Type | Cause | Response |
|-----------|-------|----------|
| LLMIntegrationError | API key missing, API error | Use fallback bot |
| JSONDecodeError | Invalid Claude response | Retry or fallback |
| APIConnectionError | Network issue | Use fallback bot |
| RateLimitError | Too many requests | Queue and retry |
| TimeoutError | Response too slow | Use fallback bot |

### Error Handling Flow

```python
try:
    response = self.client.messages.create(
        model=self.model,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
except json.JSONDecodeError as e:
    raise LLMIntegrationError(f"Failed to parse Claude response: {str(e)}")
except anthropic.APIError as e:
    raise LLMIntegrationError(f"Claude API error: {str(e)}")
except anthropic.APIConnectionError as e:
    raise LLMIntegrationError(f"Connection error: {str(e)}")
except anthropic.RateLimitError as e:
    raise LLMIntegrationError(f"Rate limited: {str(e)}")
except anthropic.APITimeoutError as e:
    raise LLMIntegrationError(f"Timeout: {str(e)}")
```

### User-Facing Error Messages

```python
# Graceful error messages shown to users
ERROR_MESSAGES = {
    "network_error": "I'm having trouble connecting. Please try again.",
    "timeout": "That took too long. Can you rephrase your question?",
    "rate_limit": "I'm a bit busy. Please wait a moment and try again.",
    "api_error": "Technical issue. Using basic mode. How can I help?",
    "unknown": "I'm sorry, I'm having trouble. Please try again later."
}
```

---

## Code Examples

### Example 1: Simple Service Inquiry

```python
# User input
user_message = "What services do you offer?"

# Claude's intent detection
{
    "intent": "service_inquiry",
    "confidence": 0.98,
    "requires_db_query": true,
    "query_type": "list_services",
    "entities": {}
}

# Database query triggered
services = Service.objects.filter(is_active=True)

# Claude's response
"Here are our available services:\n\n💇 Hair Spa (₱500)\n💇 Haircut (₱100)\n..."
```

### Example 2: Pricing with Entity Extraction

```python
# User input
user_message = "Magkano ang hair spa?"

# Claude detects service name via entity extraction
{
    "intent": "pricing",
    "confidence": 0.96,
    "entities": {
        "service_name": "hair spa"
    },
    "requires_db_query": true,
    "query_type": "get_pricing"
}

# Fuzzy matching finds service
matched_service = Service.objects.get(name="Hair Spa")

# Claude generates response
"Hair Spa costs ₱500 for 75 minutes. It's a relaxing treatment..."
```

### Example 3: Fallback to Regex Bot

```python
# Scenario: API key not configured
self.use_nlu = False  # Claude unavailable

# User input
user_message = "What's the cheapest service?"

# Skip Claude, use IntelligentChatbot
response = self.intelligent_bot.process_message(user_message)

# Response from regex-based bot
"Our cheapest service is Haircut at ₱100..."

# Confidence is lower but still helpful
"confidence": 0.8
```

---

## API Reference

### POST /api/chatbot/respond/

**Request**:
```json
{
  "message": "What services do you have?",
  "session_id": "optional-session-id"
}
```

**Response**:
```json
{
  "response": "Here are our services...",
  "intent": "service_inquiry",
  "confidence": 0.95,
  "error": null,
  "is_staff": false,
  "session_id": "session-id-123",
  "conversation_id": 456
}
```

### POST /api/chatbot/feedback/

**Request**:
```json
{
  "conversation_id": 456,
  "was_helpful": true
}
```

**Response**:
```json
{
  "success": true,
  "message": "Thank you for your feedback!"
}
```

### GET /api/chatbot/analytics/

**Parameters**: `?days=30`

**Response**:
```json
{
  "success": true,
  "data": {
    "total_conversations": 150,
    "average_satisfaction": 0.82,
    "top_intents": [
      {"intent": "pricing", "count": 45},
      {"intent": "service_inquiry", "count": 38}
    ],
    "error_rate": 0.05
  },
  "period_days": 30
}
```

---

## Performance Metrics

### Typical Response Times

| Component | Time |
|-----------|------|
| Intent Detection | 400-800ms |
| Database Query | 50-200ms |
| Response Generation | 300-600ms |
| Total Request | 800-1500ms |

### Token Usage

| Operation | Input Tokens | Output Tokens |
|-----------|--------------|---------------|
| Intent Detection | 300-500 | 150-300 |
| Response Generation | 400-600 | 200-400 |
| Average per Message | 350-550 | 175-350 |

### Cost Estimation

```
- Input: $3/1M tokens
- Output: $15/1M tokens
- 1000 messages/day
- ~500 input tokens/msg, ~250 output tokens/msg

Daily cost = (1000 * 500 * 3/1M) + (1000 * 250 * 15/1M)
           = $1.50 + $3.75 = ~$5.25/day
```

---

## Best Practices

### 1. API Key Management
✅ Store in `.env` file (not in code)
✅ Use environment variables
✅ Regenerate if exposed
❌ Don't commit API keys to git
❌ Don't share API keys

### 2. Conversation Context
✅ Include last 2-3 turns only (reduces tokens)
✅ Maintain session ID for tracking
✅ Save all conversations for analytics
❌ Don't pass entire conversation history (too many tokens)
❌ Don't share user data without consent

### 3. Error Handling
✅ Always provide fallback responses
✅ Log errors for debugging
✅ Show user-friendly messages
✅ Track error rates
❌ Don't expose API errors to users
❌ Don't retry indefinitely

### 4. Response Quality
✅ Validate responses before returning
✅ Truncate overly long responses
✅ Cite data sources
✅ Use consistent tone
❌ Don't make up information
❌ Don't promise what you can't deliver

---

## Troubleshooting

### Issue: "Claude NLU not available"

**Cause**: API key not set

**Solution**:
```bash
# Check .env file
echo $ANTHROPIC_API_KEY

# If empty, set it
export ANTHROPIC_API_KEY=sk-ant-your-key

# Restart server
python manage.py runserver
```

### Issue: "RateLimitError"

**Cause**: Too many requests to Claude API

**Solution**:
- Add request queue/throttling
- Increase API rate limit in Anthropic console
- Use fallback bot for some requests

### Issue: Responses are slow (> 3 seconds)

**Cause**: Network or Claude API delay

**Solution**:
- Check network connection
- Add timeout of 30 seconds
- Use fallback bot if timeout occurs
- Monitor Claude API status

---

## Future Enhancements

1. **Fine-Tuning**: Train Claude on salon-specific data
2. **Multi-Language**: Add more language support
3. **Voice Input**: Integrate speech-to-text
4. **Caching**: Cache common queries for faster responses
5. **Analytics**: Dashboard for conversation metrics
6. **Feedback Loop**: Use user feedback to improve responses

---

## References

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Claude Model Cards](https://docs.anthropic.com/en/docs/about-claude/models/latest)
- [Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-a-chatbot)

---

**Last Updated**: November 2025
**Version**: 1.0.0
