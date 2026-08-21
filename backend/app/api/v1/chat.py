"""
Chat API.

Provides authenticated RAG-based chat with persistent conversation history.

All document retrieval is restricted to documents owned by the
authenticated user.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import CurrentUser, DBSession
from app.common.logging.logger import get_logger
from app.models.chat_history import ChatConversation, ChatMessage
from app.services.rag_service import RAGService


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

logger = get_logger(__name__)


# ==============================================================================
# Constants
# ==============================================================================

DEFAULT_COLLECTION = "documents"

MIN_MESSAGE_LENGTH = 1
MAX_MESSAGE_LENGTH = 10_000

MIN_TOP_K = 1
MAX_TOP_K = 20

MAX_CONVERSATION_TITLE_LENGTH = 255


# ==============================================================================
# Schemas
# ==============================================================================


class ChatRequest(BaseModel):
    """Chat request payload."""

    message: str = Field(
        ...,
        min_length=MIN_MESSAGE_LENGTH,
        max_length=MAX_MESSAGE_LENGTH,
        description="User's question or instruction.",
    )

    collection_name: str = Field(
        default=DEFAULT_COLLECTION,
        min_length=1,
        max_length=100,
        description="Knowledge-base collection to search.",
    )

    top_k: int = Field(
        default=5,
        ge=MIN_TOP_K,
        le=MAX_TOP_K,
        description="Maximum number of document chunks to retrieve.",
    )

    conversation_id: UUID | None = Field(
        default=None,
        description="Existing conversation ID. Creates a new conversation when omitted.",
    )


class ChatResponse(BaseModel):
    """Chat response payload."""

    answer: str
    conversation_id: UUID


# ==============================================================================
# Helpers
# ==============================================================================


def _build_conversation_title(message: str) -> str:
    """
    Build a short conversation title from the first user message.
    """

    normalized = " ".join(message.strip().split())

    if len(normalized) <= MAX_CONVERSATION_TITLE_LENGTH:
        return normalized

    return (
        normalized[: MAX_CONVERSATION_TITLE_LENGTH - 3].rstrip()
        + "..."
    )


def _get_or_create_conversation(
    *,
    db: DBSession,
    owner_id: UUID,
    conversation_id: UUID | None,
    first_message: str,
) -> ChatConversation:
    """
    Resolve an existing owner-owned conversation or create a new one.

    A conversation ID supplied by the client is always checked against
    owner_id to prevent cross-user conversation access.
    """

    if conversation_id is not None:
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

        return conversation

    conversation = ChatConversation(
        owner_id=owner_id,
        title=_build_conversation_title(first_message),
    )

    db.add(conversation)
    db.flush()

    return conversation


# ==============================================================================
# Chat
# ==============================================================================


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with documents",
)
async def chat(
    request: ChatRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> ChatResponse:
    """
    Answer a question using retrieval-augmented generation and persist
    the conversation history.

    Retrieval is always restricted to documents owned by the
    authenticated user.

    Conversation access is also restricted to the authenticated user.
    """

    # --------------------------------------------------------------------------
    # Resolve authenticated user.
    # --------------------------------------------------------------------------

    user_id = current_user.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        )

    try:
        owner_id = UUID(str(user_id))
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        ) from exc

    # --------------------------------------------------------------------------
    # Validate collection.
    # --------------------------------------------------------------------------

    collection_name = request.collection_name.strip()

    if collection_name != DEFAULT_COLLECTION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported collection. "
                f"Only '{DEFAULT_COLLECTION}' is available."
            ),
        )

    normalized_message = request.message.strip()

    # --------------------------------------------------------------------------
    # Resolve/create conversation.
    # --------------------------------------------------------------------------

    try:
        conversation = _get_or_create_conversation(
            db=db,
            owner_id=owner_id,
            conversation_id=request.conversation_id,
            first_message=normalized_message,
        )

        user_message = ChatMessage(
            conversation_id=conversation.id,
            role="user",
            content=normalized_message,
        )

        db.add(user_message)
        db.flush()

    except HTTPException:
        raise

    except SQLAlchemyError as exc:
        db.rollback()

        logger.exception(
            "Failed to create or load chat conversation.",
            owner_id=str(owner_id),
            conversation_id=(
                str(request.conversation_id)
                if request.conversation_id
                else None
            ),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the chat conversation.",
        ) from exc

    # --------------------------------------------------------------------------
    # Execute RAG.
    # --------------------------------------------------------------------------

    try:
        rag = RAGService()

        answer = await rag.ask(
            query=normalized_message,
            owner_id=owner_id,
            collection_name=DEFAULT_COLLECTION,
            top_k=request.top_k,
        )

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()

        logger.exception(
            "RAG chat request failed.",
            owner_id=str(owner_id),
            conversation_id=str(conversation.id),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process the chat request.",
        ) from exc

    # --------------------------------------------------------------------------
    # Save assistant response.
    # --------------------------------------------------------------------------

    try:
        assistant_message = ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
        )

        db.add(assistant_message)

        # Explicitly update the conversation timestamp.
        conversation.updated_at = conversation.updated_at

        db.commit()

    except SQLAlchemyError as exc:
        db.rollback()

        logger.exception(
            "Failed to save assistant chat response.",
            owner_id=str(owner_id),
            conversation_id=str(conversation.id),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the chat response.",
        ) from exc

    # --------------------------------------------------------------------------
    # Return response.
    # --------------------------------------------------------------------------

    return ChatResponse(
        answer=answer,
        conversation_id=conversation.id,
    )


__all__ = [
    "router",
    "ChatRequest",
    "ChatResponse",
]