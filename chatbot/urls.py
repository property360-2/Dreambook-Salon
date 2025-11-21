from django.urls import path
from .views import (
    chatbot_respond_api,
    chatbot_feedback_api,
    chatbot_analytics_api,
    ChatbotInterfaceView,
    chatbot_analytics_view,
)

app_name = 'chatbot'

urlpatterns = [
    path('interface/', ChatbotInterfaceView.as_view(), name='interface'),
    path('analytics/', chatbot_analytics_view, name='analytics'),
]

# API endpoints (will be included separately under /api/)
api_urlpatterns = [
    path('chatbot/respond/', chatbot_respond_api, name='chatbot_respond'),
    path('chatbot/feedback/', chatbot_feedback_api, name='chatbot_feedback'),
    path('chatbot/analytics/', chatbot_analytics_api, name='chatbot_analytics'),
]
