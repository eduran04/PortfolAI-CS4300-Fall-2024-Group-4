"""
Authentication forms for user registration and login.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class UserRegistrationForm(UserCreationForm):
    """
    Custom user registration form that extends UserCreationForm
    with email field (required and unique).
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': (
                'mt-1 focus:ring-indigo-500 focus:border-indigo-500 '
                'block w-full shadow-sm sm:text-sm border-gray-300 '
                'dark:border-gray-600 rounded-md p-3 bg-gray-50 '
                'dark:bg-gray-700 text-gray-900 dark:text-gray-100'
            ),
            'autocomplete': 'email',
            'placeholder': 'Enter your email address'
        }),
        label='Email address'
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': (
                'mt-1 focus:ring-indigo-500 focus:border-indigo-500 '
                'block w-full shadow-sm sm:text-sm border-gray-300 '
                'dark:border-gray-600 rounded-md p-3 bg-gray-50 '
                'dark:bg-gray-700 text-gray-900 dark:text-gray-100'
            ),
            'autocomplete': 'username',
            'placeholder': 'Choose a username'
        }),
        label='Username'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': (
                'mt-1 focus:ring-indigo-500 focus:border-indigo-500 '
                'block w-full shadow-sm sm:text-sm border-gray-300 '
                'dark:border-gray-600 rounded-md p-3 bg-gray-50 '
                'dark:bg-gray-700 text-gray-900 dark:text-gray-100'
            ),
            'autocomplete': 'new-password',
            'placeholder': 'Enter a password'
        }),
        label='Password'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': (
                'mt-1 focus:ring-indigo-500 focus:border-indigo-500 '
                'block w-full shadow-sm sm:text-sm border-gray-300 '
                'dark:border-gray-600 rounded-md p-3 bg-gray-50 '
                'dark:bg-gray-700 text-gray-900 dark:text-gray-100'
            ),
            'autocomplete': 'new-password',
            'placeholder': 'Confirm your password'
        }),
        label='Password confirmation'
    )

    class Meta:
        """Meta options for UserRegistrationForm."""
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        """
        Validate that the email is unique.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        """
        Save the user and set the email.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
