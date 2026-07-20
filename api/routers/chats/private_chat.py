from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.user import User
from db.repository.private_chat_repository import PrivateChatRepository
from db.repository.message_repository import MessageRepository
from schemas.private_chat import PrivateChatResponse, OtherUserInfo
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


@router.get("/{chat_id}/messages")
async def get_messages(
    chat_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_async),
):
    logger.info(f"Get messages request {{chat_id: {chat_id}, user_id: {current_user.id_}, limit: {limit}, offset: {offset}}}")
    try:
        rep = MessageRepository(session)
        return await rep.get_by_chat_id(chat_id, limit, offset)
    except Exception as e:
        logger.error(f"Error getting messages {{chat_id: {chat_id}, user_id: {current_user.id_}}}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get messages")

