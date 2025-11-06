from django.urls import path
from .views import chatbot_respond_api, ChatbotInterfaceView

app_name = 'chatbot'

urlpatterns = [
    path('interface/', ChatbotInterfaceView.as_view(), name='interface'),
]

# API endpoint (will be included separately under /api/)
api_urlpatterns = [
    path('chatbot/respond/', chatbot_respond_api, name='chatbot_respond'),
]
