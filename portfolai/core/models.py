from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Watchlist(models.Model):
    """
    User watchlist model to store stock symbols for each user.
    Each user can have multiple stocks in their watchlist.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='watchlist_items'
    )
    symbol = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'symbol']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.symbol}"
