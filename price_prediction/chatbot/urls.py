# file: chatbot/urls.py

from django.urls import path
from . import views

app_name = 'chatbot'  # <-- ADD THIS LINE

urlpatterns = [
    # URL for the chat page itself
    path('', views.chat_page, name='chat_page'), 
    
    # URL for the API endpoint
    path('api/get-response/', views.get_api_response, name='get_api_response'),
]