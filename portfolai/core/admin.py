"""
Django admin configuration for core models.
"""
from django.contrib import admin
from .models import Watchlist

# Register your models here.


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    """Admin interface for Watchlist model."""
    list_display = ('user', 'symbol', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'symbol')
    readonly_fields = ('created_at',)
