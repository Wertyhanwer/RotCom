from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.user import User
from db.repository.call_repository import CallRepository
from schemas.call import CallIn, CallResponse
from dependencies import get_session_async
from dependencies.auth import get_current_user

import logging
logger = logging.getLogger("messenger.calls")

router = APIRouter(prefix="/chats/private", tags=["calls"])


@router.post("/{chat_id}/calls", response_model=CallResponse)
async def create_call(
    chat_id: int,
    call_in: CallIn,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_async),
):
    logger.info(f"Create call request {{chat_id: {chat_id}, caller_id: {current_user.id_}}}")
    try:
        rep = CallRepository(session)
        return await rep.create(chat_id, current_user.id_, call_in.status, call_in.duration)
    except Exception as e:
        logger.error(f"Error creating call {{chat_id: {chat_id}, caller_id: {current_user.id_}}}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create call")


@router.get("/{chat_id}/calls", response_model=list[CallResponse])
async def get_calls(
    chat_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_async),
):
    logger.info(f"Get calls request {{chat_id: {chat_id}, user_id: {current_user.id_}}}")
    try:
        rep = CallRepository(session)
        return await rep.get_by_chat_id(chat_id, limit, offset)
    except Exception as e:
        logger.error(f"Error getting calls {{chat_id: {chat_id}, user_id: {current_user.id_}}}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get calls")
