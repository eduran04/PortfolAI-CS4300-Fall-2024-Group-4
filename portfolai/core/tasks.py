"""
Celery Tasks for PortfolAI Chat Service
========================================

Background task processing for AI chat requests.
This module is optional - the chat service works synchronously if Celery is not configured.
"""

import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

# Try to import Celery, but don't fail if it's not installed
try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    # Create a dummy decorator if Celery is not available
    def shared_task(*args, **kwargs):
        """Dummy decorator when Celery is not available."""
        def decorator(func):
            return func
        return decorator


@shared_task(bind=True, max_retries=3)
def process_chat_message_async(self, user_id, session_id, assistant_message_id):
    """
    Celery task to process chat messages asynchronously.
    
    This task handles the AI processing in the background, allowing
    the API to return immediately with a pending status.
    
    Args:
        user_id (int): ID of the user sending the message
        session_id (int): ID of the chat session
        assistant_message_id (int): ID of the pending assistant message to update
        
    Returns:
        dict: Result containing conversation_id, response, and status
    """
    from django.contrib.auth.models import User
    from .models import AIChatSession, AIRequest
    from .services import ChatService
    from django.core.exceptions import ValidationError
    
    try:
        # Get user and session
        user = User.objects.get(id=user_id)
        session = AIChatSession.objects.get(id=session_id, user=user)
        assistant_message = AIRequest.objects.get(
            id=assistant_message_id,
            session=session
        )
        
        # Initialize chat service
        chat_service = ChatService()
        
        # Format messages for AI
        ai_messages = chat_service.format_messages_for_ai(session, include_system=True)
        
        # Call OpenAI API
        ai_response = chat_service._call_openai_api(ai_messages)
        
        # Update assistant message with response
        assistant_message.content = ai_response
        assistant_message.status = AIRequest.COMPLETED
        assistant_message.save()
        
        # Update session timestamp
        session.updated_at = timezone.now()
        session.save(update_fields=['updated_at'])
        
        logger.info(
            f"Successfully processed async message for user {user.username} "
            f"in session {session.id}"
        )
        
        return {
            'conversation_id': session.id,
            'response': ai_response,
            'status': 'success'
        }
        
    except (User.DoesNotExist, AIChatSession.DoesNotExist, AIRequest.DoesNotExist) as e:
        logger.error(f"Resource not found for async chat processing: {str(e)}")
        raise
    except ValidationError as e:
        logger.warning(f"Validation error in async chat: {str(e)}")
        raise
    except Exception as e:
        logger.error(
            f"Error in async chat processing: {str(e)}",
            exc_info=True
        )
        
        # Update assistant message with error
        try:
            assistant_message = AIRequest.objects.get(id=assistant_message_id)
            error_msg = "I apologize, but I'm having trouble processing your request right now. Please try again later."
            assistant_message.content = error_msg
            assistant_message.status = AIRequest.FAILED
            assistant_message.error_message = str(e)
            assistant_message.save()
        except Exception:
            pass  # Ignore errors when updating error message
        
        # Retry on certain exceptions
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=2 ** self.request.retries)
        raise

