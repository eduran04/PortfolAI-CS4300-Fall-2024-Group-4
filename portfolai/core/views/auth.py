"""
Demo authentication views.
"""
from django.contrib.auth.views import LoginView
from django.conf import settings


class DemoLoginView(LoginView):
    """Login view that exposes the demo username in the template context."""
    template_name = 'registration/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['demo_username'] = settings.DEMO_USERNAME
        return context
