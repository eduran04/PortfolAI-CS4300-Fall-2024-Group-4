from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Watchlist(models.Model):
    """
    User watchlist model to store stock symbols for each user.
    Each user can have multiple stocks in their watchlist.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist_items')
    symbol = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'symbol']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.symbol}"

class AIChatSession(models.Model):
    """
    Represents an AI chat conversation session.
    
    Each session belongs to a user and can contain multiple messages.
    Sessions can be marked as inactive (soft delete) for archival purposes.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_sessions',
        help_text='User who owns this conversation session'
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Optional title for the conversation'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this session is active (soft delete)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active', '-updated_at']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = 'AI Chat Session'
        verbose_name_plural = 'AI Chat Sessions'
    
    def __str__(self):
        """Return string representation of the session."""
        title = self.title or 'Untitled Conversation'
        return f"{self.user.username} - {title} ({self.id})"


class AIRequest(models.Model):
    """
    Represents a message in an AI chat conversation.
    
    Each request can be a user message, assistant response, or system message.
    The status field tracks the processing state of AI requests.
    """
    
    # Status choices for AI request processing
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'complete'
    FAILED = 'failed'
    
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (RUNNING, 'Running'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    )
    
    # Role choices for message types
    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'
    ROLE_SYSTEM = 'system'
    
    ROLE_CHOICES = (
        (ROLE_USER, 'User'),
        (ROLE_ASSISTANT, 'Assistant'),
        (ROLE_SYSTEM, 'System'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_requests',
        help_text='User who sent this message'
    )
    session = models.ForeignKey(
        AIChatSession,
        on_delete=models.CASCADE,
        related_name='requests',
        help_text='Chat session this message belongs to'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_USER,
        help_text='Role of the message sender (user, assistant, or system)'
    )
    content = models.TextField(
        help_text='The actual message content'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
        help_text='Processing status of the AI request'
    )
    # Keep legacy JSON fields for backward compatibility if needed
    message = models.JSONField(
        null=True,
        blank=True,
        help_text='Legacy JSON field for message data (deprecated)'
    )
    response = models.JSONField(
        null=True,
        blank=True,
        help_text='Legacy JSON field for response data (deprecated)'
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text='Error message if request failed'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status']),
        ]
        verbose_name = 'AI Request'
        verbose_name_plural = 'AI Requests'
    
    def __str__(self):
        """Return string representation of the request."""
        content_preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.role} - {content_preview} ({self.status})"
    
