from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import Rule


@csrf_exempt
@require_http_methods(["POST"])
def chatbot_respond_api(request):
    """
    API endpoint for chatbot responses.

    POST /api/chatbot/respond/
    Body: {"message": "user message"}
    Returns: {"response": "bot response", "matched_rule": int or null}
    """
    try:
        # Parse request body
        body = json.loads(request.body)
        user_message = body.get('message', '').strip()

        if not user_message:
            return JsonResponse({
                'error': 'Message is required',
                'response': None,
                'matched_rule': None
            }, status=400)

        # Find matching rule (first match wins, ordered by priority)
        matched_rule = None
        for rule in Rule.objects.filter(is_active=True).order_by('-priority', 'keyword'):
            if rule.matches(user_message):
                matched_rule = rule
                break

        if matched_rule:
            return JsonResponse({
                'response': matched_rule.response,
                'matched_rule': matched_rule.id,
                'error': None
            })
        else:
            # Default response when no rule matches
            default_response = (
                "I'm not sure how to help with that. "
                "You can ask me about our services, hours, booking, or contact information!"
            )
            return JsonResponse({
                'response': default_response,
                'matched_rule': None,
                'error': None
            })

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body',
            'response': None,
            'matched_rule': None
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Server error: {str(e)}',
            'response': None,
            'matched_rule': None
        }, status=500)


class ChatbotInterfaceView(View):
    """Simple web interface for testing the chatbot."""

    def get(self, request):
        """Show chatbot interface."""
        context = {
            'available_rules': Rule.objects.filter(is_active=True).order_by('-priority')
        }
        return render(request, 'pages/chatbot_interface.html', context)
