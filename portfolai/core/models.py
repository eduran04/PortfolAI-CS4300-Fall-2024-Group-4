"""
Core models for the PortfolAI application.
"""
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Watchlist(models.Model):  # pylint: disable=too-few-public-methods
    """
    User watchlist model to store stock symbols for each user.
    Each user can have multiple stocks in their watchlist.
    Django model - data class with minimal public methods is acceptable.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='watchlist_items'
    )
    symbol = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta options for Watchlist model."""
        unique_together = ['user', 'symbol']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.symbol}"  # pylint: disable=no-member
