"""
URL configuration for core app authentication and chat views.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import chat_api

urlpatterns = [
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    # Chat API URLs
    path("api/chat/", chat_api, name="chat_api"),
    path("api/chatbot/", chat_api, name="chatbot"),
]
