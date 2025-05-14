from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from beanie import PydanticObjectId

from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.session import Conversation
from app.models.customer import Customer
from app.models.message import Message
from app.schemas.conversation import (
    ConversationCreate, 
    ConversationRead,
    ConversationUpdate,
    MessageCreate,
    MessageRead
)
from app.tasks.conversation_tasks import process_ai_message

router = APIRouter()


@router.get("/", response_model=List[ConversationRead])
async def list_conversations(
    current_user: User = Depends(get_current_active_user),
    limit: int = 10,
    skip: int = 0,
) -> Any:
    """
    List conversations for the current user
    
    Args:
        current_user: Current authenticated user
        limit: Maximum number of conversations to return
        skip: Number of conversations to skip
        
    Returns:
        List of conversations
    """
    return await Conversation.find(
        Conversation.user.id == current_user.id
    ).sort(-Conversation.updated_at).skip(skip).limit(limit).to_list()


@router.post("/", response_model=ConversationRead)
async def create_conversation(
    conversation_in: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new conversation
    
    Args:
        conversation_in: Conversation creation data
        current_user: Current authenticated user
        
    Returns:
        Created conversation
        
    Raises:
        HTTPException: If customer is not found
    """
    # Find the customer
    customer = await Customer.get(conversation_in.customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )
    
    # Create the conversation
    conversation = Conversation(
        title=conversation_in.title,
        user=current_user,
        customer=customer,
        tags=conversation_in.tags,
    )
    await conversation.create()
    
    return conversation


@router.get("/{conversation_id}", response_model=ConversationRead)
async def get_conversation(
    conversation_id: PydanticObjectId,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a conversation by ID
    
    Args:
        conversation_id: Conversation ID
        current_user: Current authenticated user
        
    Returns:
        Conversation details
        
    Raises:
        HTTPException: If conversation is not found or doesn't belong to the user
    """
    conversation = await Conversation.get(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    
    # Check if the conversation belongs to the user
    if conversation.user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return conversation


@router.post("/{conversation_id}/messages", response_model=MessageRead)
async def create_message(
    conversation_id: PydanticObjectId,
    message_in: MessageCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new message in a conversation
    
    Args:
        conversation_id: Conversation ID
        message_in: Message creation data
        current_user: Current authenticated user
        
    Returns:
        Created message
        
    Raises:
        HTTPException: If conversation is not found or doesn't belong to the user
    """
    conversation = await Conversation.get(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    
    # Check if the conversation belongs to the user
    if conversation.user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Create the message
    message = await conversation.add_message(
        content=message_in.content,
        sender_type="user",
        sender_id=current_user.id
    )
    
    # Process the message with AI in the background
    # Note: This should be an actual background task
    # We're calling the function directly for simplicity,
    # but in production you'd use celery_app.send_task
    ai_task = process_ai_message.delay(
        conversation_id=str(conversation.id),
        message_content=message_in.content,
        context={
            "customer_info": {
                "name": conversation.customer.full_name,
                "company": conversation.customer.company,
            }
        }
    )
    
    return message


@router.get("/{conversation_id}/messages", response_model=List[MessageRead])
async def list_messages(
    conversation_id: PydanticObjectId,
    current_user: User = Depends(get_current_active_user),
    limit: int = 50,
    skip: int = 0,
) -> Any:
    """
    List messages in a conversation
    
    Args:
        conversation_id: Conversation ID
        current_user: Current authenticated user
        limit: Maximum number of messages to return
        skip: Number of messages to skip
        
    Returns:
        List of messages
        
    Raises:
        HTTPException: If conversation is not found or doesn't belong to the user
    """
    conversation = await Conversation.get(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    
    # Check if the conversation belongs to the user
    if conversation.user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Get messages
    messages = await Message.find(
        Message.conversation.id == conversation.id
    ).sort(Message.created_at).skip(skip).limit(limit).to_list()
    
    return messages 