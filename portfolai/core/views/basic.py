"""
Basic Views - Landing Page, Dashboard, and API Health Check
============================================================

Core application views for user interface and basic API testing.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response


def landing(request):
    """
    Landing page view - Feature: User Interface
    Renders the main landing page with application introduction
    """
    return render(request, "landing.html")


@login_required
def trading_dashboard(request):
    """
    Trading dashboard view - Feature: Main Application Interface
    Renders the main trading dashboard with all features
    Requires user authentication.
    """
    return render(request, "home.html")


@api_view(["GET"])
def hello_api(request):
    """
    Basic API connectivity test - Feature: API Health Check
    Simple endpoint to verify API functionality
    Returns: {"message": "Hello from Django + Basecoat + DRF!"}
    """
    return Response({"message": "Hello from Django + Basecoat + DRF!"})

