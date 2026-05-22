"""
Create or update the shared demo login account.
Safe to run on every deploy (idempotent).
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    """Create or update the shared demo login user."""
    help = "Ensure the shared demo user exists with the configured password."

    def handle(self, *args, **options):
        username = settings.DEMO_USERNAME
        password = settings.DEMO_PASSWORD

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@portfolai.demo"},
        )
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created demo user '{username}'"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated demo user '{username}'"))
