"""
Chat Views - PortfolAI Chatbot API
===================================

Chatbot endpoint for AI-powered user interactions with conversation tracking.
"""

from django.http import JsonResponse
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view
import json
import logging
from ..services import ChatService

logger = logging.getLogger(__name__)


@api_view(["POST"])
def chat_api(request):
    """
    PortfolAI Chatbot API Endpoint
    
    Handles authenticated user chat messages with full conversation tracking.
    Supports conversation continuation via optional conversation_id.
    
    Request Body:
        - message (str, required): User message content
        - conversation_id (int, optional): ID of conversation to continue
        
    Returns:
        - conversation_id (int): ID of the conversation
        - response (str): AI assistant response
        - status (str): 'success' or 'error'
        - fallback (bool, optional): True if fallback response used
    """
    # Check authentication
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )
    
    # Parse request body
    try:
        data = json.loads(request.body.decode("utf-8"))
        user_message = data.get("message", "").strip()
        conversation_id = data.get("conversation_id")
        
        # Validate conversation_id if provided
        if conversation_id is not None:
            try:
                conversation_id = int(conversation_id)
            except (ValueError, TypeError):
                return JsonResponse(
                    {"error": "Invalid conversation_id format"},
                    status=400
                )
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.warning(f"Invalid JSON in chat request: {e}")
        return JsonResponse(
            {"error": "Invalid JSON format"},
            status=400
        )
    
    # Validate message
    if not user_message:
        return JsonResponse(
            {"error": "Message cannot be empty"},
            status=400
        )
    
    # Initialize chat service
    chat_service = ChatService()
    
    try:
        # Process message through chat service
        result = chat_service.send_message(
            user=request.user,
            content=user_message,
            conversation_id=conversation_id
        )
        
        # Return success response
        return JsonResponse({
            "conversation_id": result.get("conversation_id"),
            "response": result.get("response"),
            "status": result.get("status", "success")
        }, status=200)
        
    except ValidationError as e:
        # Handle validation errors (rate limit, sanitization, etc.)
        logger.warning(
            f"Validation error for user {request.user.username}: {str(e)}"
        )
        return JsonResponse(
            {"error": str(e)},
            status=400
        )
    except Exception as e:
        # Handle unexpected errors
        logger.error(
            f"Unexpected error in chat API for user {request.user.username}: {str(e)}",
            exc_info=True
        )
        
        # Check if OpenAI client is available for fallback
        from django.conf import settings
        from ._clients import openai_client
        if not getattr(settings, "OPENAI_API_KEY", None) or openai_client is None:
            return JsonResponse(
                {
                    "response": "(Fallback) You said: " + user_message,
                    "fallback": True,
                    "status": "fallback"
                },
                status=200
            )
        
        # Return generic error message (don't expose internal errors)
        return JsonResponse(
            {
                "error": "An error occurred while processing your message. Please try again later.",
                "status": "error"
            },
            status=500
        )

