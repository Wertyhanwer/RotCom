from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pymongo.asynchronous.database import AsyncDatabase
from pydantic import NonNegativeInt

from db.models.user import User
from db.repository.chat_event_repository import ChatEventRepository
from schemas.call import CallStatus, CallEvent, CallResponse
from dependencies import get_session_async, get_mongo_db
from dependencies.auth import get_current_user
from routers.chats.private_chat import parse_cursor, get_member_chat_or_404
from services.chat_events import save_chat_event

import logging
logger = logging.getLogger("messenger.calls")

router = APIRouter(prefix="/chats/private", tags=["calls"])


@router.post("/{chat_id}/calls", response_model=CallResponse)
async def create_call(
    chat_id: int,
    status: CallStatus,
    duration: NonNegativeInt,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_async),
    mongo_db: AsyncDatabase = Depends(get_mongo_db),
):
    logger.info(f"Create call request {{chat_id: {chat_id}, caller_id: {current_user.id_}}}")
    chat = await get_member_chat_or_404(chat_id, current_user, session)
    other_user_id = chat.user2_id if chat.user1_id == current_user.id_ else chat.user1_id
    event = CallEvent(event_type="call", to_user_id=other_user_id, status=status, duration=duration)
    try:
        document = await save_chat_event(session, mongo_db, chat, current_user.id_, event)
        return CallResponse.model_validate(document)
    except Exception as e:
        logger.error(f"Error creating call {{chat_id: {chat_id}, caller_id: {current_user.id_}}}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create call")


@router.get("/{chat_id}/calls", response_model=list[CallResponse])
async def get_calls(
    chat_id: int,
    limit: int = Query(50, ge=1, le=100),
    before: str | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_async),
    mongo_db: AsyncDatabase = Depends(get_mongo_db),
):
    logger.info(f"Get calls request {{chat_id: {chat_id}, user_id: {current_user.id_}}}")
    before_id = parse_cursor(before)
    await get_member_chat_or_404(chat_id, current_user, session)
    try:
        rep = ChatEventRepository(mongo_db)
        documents = await rep.get_history(chat_id, limit, before_id, event_type="call")
        return [CallResponse.model_validate(document) for document in documents]
    except Exception as e:
        logger.error(f"Error getting calls {{chat_id: {chat_id}, user_id: {current_user.id_}}}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get calls")
