from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
import json
import uuid
from .models import Rule, ConversationHistory
from .intelligent_service import IntelligentChatbotService
from .analytics import ChatbotAnalytics


@csrf_exempt
@require_http_methods(["POST"])
def chatbot_respond_api(request):
    """
    Enhanced intelligent chatbot API endpoint with:
    - Claude NLU for natural language understanding
    - Conversation history for context
    - Fuzzy matching for typo tolerance
    - Database queries and role-based responses

    POST /api/chatbot/respond/
    Body: {
        "message": "user message",
        "session_id": "optional session id"
    }
    Returns: {
        "response": "bot response",
        "intent": "detected intent",
        "confidence": 0.0-1.0,
        "error": null or error message
    }
    """
    try:
        # Parse request body
        body = json.loads(request.body)
        user_message = body.get('message', '').strip()
        session_id = body.get('session_id')

        if not user_message:
            return JsonResponse({
                'error': 'Message is required',
                'response': None,
                'intent': None,
                'confidence': 0.0,
            }, status=400)

        # Generate session ID if not provided (for conversation tracking)
        if not session_id:
            session_id = request.session.session_key
            if not session_id:
                session_id = str(uuid.uuid4())

        # Use intelligent chatbot with GROQ + database queries
        user = request.user if request.user.is_authenticated else None
        bot = IntelligentChatbotService(user=user, session_id=session_id)

        # Process message through intelligent system
        result = bot.process_message(user_message, save_history=True)

        # Get the latest conversation record (just saved)
        conversation_record = ConversationHistory.objects.filter(
            session_id=session_id
        ).order_by('-created_at').first()

        return JsonResponse({
            'response': result['response'],
            'intent': result['intent'],
            'confidence': result['confidence'],
            'error': result['error'],
            'tools_used': result.get('tools_used', []),
            'is_staff': bot.is_staff,
            'session_id': session_id,
            'conversation_id': conversation_record.id if conversation_record else None,
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body',
            'response': None,
            'intent': None,
            'confidence': 0.0,
        }, status=400)
    except Exception as e:
        # Log error but provide fallback
        print(f"Chatbot API error: {str(e)}")
        return JsonResponse({
            'error': f'Server error: {str(e)}',
            'response': 'I apologize, but I encountered an error. Please try again.',
            'intent': 'error',
            'confidence': 0.0,
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def chatbot_feedback_api(request):
    """
    Accept user feedback on chatbot responses.

    POST /api/chatbot/feedback/
    Body: {
        "conversation_id": "id",
        "was_helpful": true/false
    }
    """
    try:
        body = json.loads(request.body)
        conversation_id = body.get('conversation_id')
        was_helpful = body.get('was_helpful')

        if not conversation_id or was_helpful is None:
            return JsonResponse({
                'error': 'conversation_id and was_helpful are required',
            }, status=400)

        # Update conversation feedback
        conversation = ConversationHistory.objects.filter(id=conversation_id).first()
        if not conversation:
            return JsonResponse({
                'error': 'Conversation not found',
            }, status=404)

        conversation.was_helpful = was_helpful
        conversation.save()

        return JsonResponse({
            'success': True,
            'message': 'Thank you for your feedback!',
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON',
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Error: {str(e)}',
        }, status=500)


@login_required
@require_http_methods(["GET"])
def chatbot_analytics_api(request):
    """
    Get chatbot analytics (staff/admin only).

    GET /api/chatbot/analytics/?days=30
    """
    # Check permissions
    if not (request.user.is_authenticated and request.user.role in ['ADMIN', 'STAFF']):
        return JsonResponse({
            'error': 'Only staff and admin can view analytics',
        }, status=403)

    try:
        days = int(request.GET.get('days', 30))
        days = max(1, min(days, 365))  # Limit to 1-365 days

        # Build analytics data
        dashboard_data = ChatbotAnalytics.get_dashboard_data()

        # Recalculate with specified days
        dashboard_data['overall_stats'] = ChatbotAnalytics.get_overall_stats(days=days)
        dashboard_data['intent_distribution'] = ChatbotAnalytics.get_intent_distribution(days=days)
        dashboard_data['confidence_distribution'] = ChatbotAnalytics.get_confidence_distribution(days=days)
        dashboard_data['user_satisfaction'] = ChatbotAnalytics.get_user_satisfaction(days=days)
        dashboard_data['session_analytics'] = ChatbotAnalytics.get_session_analytics(days=days)
        dashboard_data['trends'] = ChatbotAnalytics.get_trends(days=days)
        dashboard_data['problematic_intents'] = ChatbotAnalytics.get_problematic_intents(days=days)

        return JsonResponse({
            'success': True,
            'data': dashboard_data,
            'period_days': days,
        })

    except ValueError:
        return JsonResponse({
            'error': 'days parameter must be an integer',
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Error: {str(e)}',
        }, status=500)


class ChatbotInterfaceView(View):
    """Simple web interface for testing the chatbot."""

    def get(self, request):
        """Show chatbot interface."""
        context = {
            'available_rules': Rule.objects.filter(is_active=True).order_by('-priority')
        }
        return render(request, 'pages/chatbot_interface.html', context)


@login_required
def chatbot_analytics_view(request):
    """
    Staff/Admin view for chatbot analytics dashboard.
    Shows performance metrics, recommendations, and insights.
    """
    # Check permissions
    if not (request.user.is_authenticated and request.user.role in ['ADMIN', 'STAFF']):
        return JsonResponse({
            'error': 'Only staff and admin can view analytics'
        }, status=403)

    # Get analytics data
    analytics_data = ChatbotAnalytics.get_dashboard_data()

    context = {
        'analytics': analytics_data,
        'page_title': 'Chatbot Analytics',
    }
    return render(request, 'pages/chatbot_analytics.html', context)
