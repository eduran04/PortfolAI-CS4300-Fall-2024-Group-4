"""
Django Admin Configuration for PortfolAI Core Models
=====================================================

Admin interface configuration for Watchlist, AIChatSession, and AIRequest models.
"""

from django.contrib import admin
from .models import Watchlist, AIChatSession, AIRequest


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    """Admin interface for Watchlist model."""
    list_display = ('user', 'symbol', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'symbol')
    readonly_fields = ('created_at',)


class AIRequestInline(admin.TabularInline):
    """Inline admin for AIRequest within AIChatSession."""
    model = AIRequest
    extra = 0
    readonly_fields = ('created_at', 'updated_at', 'status')
    fields = ('role', 'content', 'status', 'created_at', 'updated_at')
    can_delete = False


@admin.register(AIChatSession)
class AIChatSessionAdmin(admin.ModelAdmin):
    """Admin interface for AIChatSession model."""
    list_display = ('id', 'user', 'title', 'is_active', 'created_at', 'updated_at', 'message_count')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('user__username', 'title')
    readonly_fields = ('created_at', 'updated_at', 'message_count')
    fields = ('user', 'title', 'is_active', 'created_at', 'updated_at', 'message_count')
    inlines = [AIRequestInline]
    
    def message_count(self, obj):
        """Return the number of messages in this session."""
        return obj.requests.count()
    message_count.short_description = 'Messages'


@admin.register(AIRequest)
class AIRequestAdmin(admin.ModelAdmin):
    """Admin interface for AIRequest model."""
    list_display = ('id', 'user', 'session', 'role', 'status', 'content_preview', 'created_at')
    list_filter = ('role', 'status', 'created_at')
    search_fields = ('user__username', 'content', 'session__title')
    readonly_fields = ('created_at', 'updated_at')
    fields = ('user', 'session', 'role', 'content', 'status', 'error_message', 'created_at', 'updated_at')
    raw_id_fields = ('user', 'session')
    
    def content_preview(self, obj):
        """Return a preview of the message content."""
        if len(obj.content) > 100:
            return obj.content[:100] + '...'
        return obj.content
    content_preview.short_description = 'Content Preview'