from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import TypeAdapter

from db.models.user import User
from db.repository.private_chat_repository import PrivateChatRepository
from db.repository.chat_history_repository import ChatHistoryRepository
from schemas.private_chat import PrivateChatResponse, OtherUserInfo
from schemas.chat_history import HistoryItem
from dependencies import get_session_async
from dependencies.auth import get_current_user

import logging
logger = logging.getLogger("messenger.chats")

router = APIRouter(prefix="/chats/private", tags=["chats"])


@router.get("/", response_model=list[PrivateChatResponse])
async def get_chats(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_async),
):
    logger.info(f"Get chats request {{user_id: {current_user.id_}, limit: {limit}, offset: {offset}}}")
    try:
        rep = PrivateChatRepository(session)
        rows = await rep.get_all_by_user(current_user.id_, limit, offset)
        return [
            PrivateChatResponse(
                id_=chat.id_,
                created_at=chat.created_at,
                last_event_at=chat.last_event_at,
                last_message=chat.last_message,
                other_user=OtherUserInfo.model_validate(user),
            )
            for chat, user in rows
        ]
    except Exception as e:
        logger.error(f"Error getting chats {{user_id: {current_user.id_}}}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chats")



history_adapter = TypeAdapter(list[HistoryItem])


@router.get("/{chat_id}/history")
async def get_history(
    chat_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_async),
):
    logger.info(f"Get history request {{chat_id: {chat_id}, user_id: {current_user.id_}}}")
    try:
        rep = ChatHistoryRepository(session)
        rows = await rep.get_history(chat_id, limit, offset)
        return history_adapter.validate_python([dict(row) for row in rows])
    except Exception as e:
        logger.error(f"Error getting history {{chat_id: {chat_id}, user_id: {current_user.id_}}}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get history")

