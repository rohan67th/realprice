from django.db import models

# Create your models here.
# chatbot/models.py

from django.db import models
from django.conf import settings # If you have user authentication

class Conversation(models.Model):
    """
    Represents a single chat session.
    If you have users, you can add a ForeignKey to the User model.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    """
    title = models.CharField(max_length=255, default="New Conversation")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id} started at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class ChatMessage(models.Model):
    """ Represents a single message within a conversation. """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI'),
    ]

    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=4, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_role_display()} message at {self.timestamp.strftime('%H:%M')}"