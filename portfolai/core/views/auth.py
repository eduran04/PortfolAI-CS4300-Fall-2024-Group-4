"""
Authentication Views
====================

User registration and authentication views.
"""

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from ..forms import UserRegistrationForm


class SignUpView(CreateView):  # pylint: disable=too-many-ancestors
    """
    User registration view.
    Creates a new user account with email (required and unique).
    Redirects to login page after successful registration.
    Django framework pattern requires extending CreateView.
    """
    form_class = UserRegistrationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        """
        Save the user and redirect to login page.
        """
        form.save()
        messages.success(self.request, 'Account created successfully! Please log in to continue.')
        return super().form_valid(form)
