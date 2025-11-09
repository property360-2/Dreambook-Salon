from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import Rule
from .intelligent_bot import IntelligentChatbot


@csrf_exempt
@require_http_methods(["POST"])
def chatbot_respond_api(request):
    """
    Intelligent chatbot API endpoint with database queries and role-based responses.

    POST /api/chatbot/respond/
    Body: {"message": "user message"}
    Returns: {"response": "bot response", "intent": "detected_intent"}
    """
    try:
        # Parse request body
        body = json.loads(request.body)
        user_message = body.get('message', '').strip()

        if not user_message:
            return JsonResponse({
                'error': 'Message is required',
                'response': None,
            }, status=400)

        # Use intelligent chatbot with role-based responses
        bot = IntelligentChatbot(user=request.user if request.user.is_authenticated else None)
        response = bot.process_message(user_message)

        return JsonResponse({
            'response': response,
            'error': None,
            'is_staff': bot.is_staff,
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body',
            'response': None,
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Server error: {str(e)}',
            'response': None,
        }, status=500)


class ChatbotInterfaceView(View):
    """Simple web interface for testing the chatbot."""

    def get(self, request):
        """Show chatbot interface."""
        context = {
            'available_rules': Rule.objects.filter(is_active=True).order_by('-priority')
        }
        return render(request, 'pages/chatbot_interface.html', context)
