"""
Chat history API.

Provides authenticated access to chat conversations and messages.
All records are strictly restricted to the authenticated user.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, DBSession
from app.models.chat_history import ChatConversation


router = APIRouter(
    prefix="/chat/history",
    tags=["Chat History"],
)


# ==============================================================================
# Response Schemas
# ==============================================================================


class ChatHistoryItem(BaseModel):
    """Summary of a chat conversation."""

    id: UUID
    title: str
    created_at: str
    updated_at: str


class ChatMessageResponse(BaseModel):
    """Single chat message."""

    id: UUID
    role: str
    content: str
    created_at: str


class ChatHistoryDetail(BaseModel):
    """Conversation with all messages."""

    id: UUID
    title: str
    created_at: str
    updated_at: str
    messages: list[ChatMessageResponse]


# ==============================================================================
# Helpers
# ==============================================================================


def get_owner_id(current_user: dict) -> UUID:
    """
    Extract and validate the authenticated user's UUID.
    """

    user_id = current_user.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        )

    try:
        return UUID(str(user_id))
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        ) from exc


# ==============================================================================
# List Conversations
# ==============================================================================


@router.get(
    "",
    response_model=list[ChatHistoryItem],
    summary="Get chat history",
)
def get_chat_history(
    db: DBSession,
    current_user: CurrentUser,
) -> list[ChatHistoryItem]:
    """
    Return all conversations belonging to the authenticated user.

    Conversations belonging to other users are never returned.
    """

    owner_id = get_owner_id(current_user)

    conversations = (
        db.query(ChatConversation)
        .filter(ChatConversation.owner_id == owner_id)
        .order_by(ChatConversation.updated_at.desc())
        .all()
    )

    return [
        ChatHistoryItem(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
        )
        for conversation in conversations
    ]


# ==============================================================================
# Get Conversation
# ==============================================================================


@router.get(
    "/{conversation_id}",
    response_model=ChatHistoryDetail,
    summary="Get chat conversation",
)
def get_chat_conversation(
    conversation_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> ChatHistoryDetail:
    """
    Return one conversation and all of its messages.

    The conversation must belong to the authenticated user.
    """

    owner_id = get_owner_id(current_user)

    conversation = (
        db.query(ChatConversation)
        .filter(
            ChatConversation.id == conversation_id,
            ChatConversation.owner_id == owner_id,
        )
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    return ChatHistoryDetail(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
        messages=[
            ChatMessageResponse(
                id=message.id,
                role=message.role,
                content=message.content,
                created_at=message.created_at.isoformat(),
            )
            for message in conversation.messages
        ],
    )


# ==============================================================================
# Delete Conversation
# ==============================================================================


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete chat conversation",
)
def delete_chat_conversation(
    conversation_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    """
    Delete one conversation and all associated messages.

    The conversation must belong to the authenticated user.
    """

    owner_id = get_owner_id(current_user)

    conversation = (
        db.query(ChatConversation)
        .filter(
            ChatConversation.id == conversation_id,
            ChatConversation.owner_id == owner_id,
        )
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    db.delete(conversation)
    db.commit()
