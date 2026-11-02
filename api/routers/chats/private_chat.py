from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pymongo.asynchronous.database import AsyncDatabase
from bson import ObjectId

from db.models.user import User
from db.repository.private_chat_repository import PrivateChatRepository
from db.repository.chat_event_repository import ChatEventRepository
from schemas.private_chat import PrivateChatResponse, OtherUserInfo
from schemas.chat_history import HistoryItem, history_adapter
from dependencies import get_session_async, get_mongo_db
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


def parse_cursor(before: str | None) -> ObjectId | None:
    if before is None:
        return None
    if not ObjectId.is_valid(before):
        raise HTTPException(status_code=400, detail="Invalid cursor")
    return ObjectId(before)


async def get_member_chat_or_404(chat_id: int, user: User, session: AsyncSession):
    chat = await PrivateChatRepository(session).get_by_id_for_user(chat_id, user.id_)
    if chat is None:
        # 404, а не 403 — не раскрываем, что чат с таким id существует
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.get("/{chat_id}/history", response_model=list[HistoryItem])
async def get_history(
    chat_id: int,
    limit: int = Query(50, ge=1, le=100),
    before: str | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_async),
    mongo_db: AsyncDatabase = Depends(get_mongo_db),
):
    logger.info(f"Get history request {{chat_id: {chat_id}, user_id: {current_user.id_}, before: {before}}}")
    before_id = parse_cursor(before)
    await get_member_chat_or_404(chat_id, current_user, session)
    try:
        rep = ChatEventRepository(mongo_db)
        documents = await rep.get_history(chat_id, limit, before_id)
        return history_adapter.validate_python(documents)
    except Exception as e:
        logger.error(f"Error getting history {{chat_id: {chat_id}, user_id: {current_user.id_}}}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get history")
