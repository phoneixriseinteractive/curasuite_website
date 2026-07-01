"""CuraSuite — API v1 URLs"""
from django.urls import path
from apps.integrations.chatbot_views import chatbot_message

app_name = "api_v1"

urlpatterns = [
    path("chatbot/message/", chatbot_message, name="chatbot_message"),
]
