import json
from fastapi import APIRouter, WebSocket
import logging

from schemas.message import MessageIn

from db.repository.message_repository import MessageRepository
from routers.service.JWT.token_decode import decode_token
from routers.service.JWT.token_payload_model import TokenPayloadModel
from db.repository.private_chat_repository import PrivateChatRepository
from db.repository.user_repository import UserRepository
from dependencies.db import get_session
from .connection_manager import connection_manager

router = APIRouter(prefix="/ws", tags=["ws"])

logger = logging.getLogger("messenger.ws")


@router.websocket("/")
async def chat(websocket: WebSocket, token: str):
    await websocket.accept()

    token_model: TokenPayloadModel = decode_token(token)
    current_user_id = int(token_model.sub)

    async with get_session() as session:
        user_rep = UserRepository(session)
        current_user = await user_rep.get_by_id(current_user_id)
        if not current_user:
            logger.info(f"Ws connection closed! user {current_user_id} does not exist")
            await websocket.close(code=1008)
            return


    await connection_manager.connect(current_user.id_, websocket)
    logger.info(f"Ws connected: user_id={current_user_id}")
    
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = MessageIn.model_validate_json(raw)
            except Exception:
                await websocket.send_text(json.dumps({"error": "invalid message format"}))
                continue

            to_user_id = msg.to_user_id
            content = msg.content

            async with get_session() as session:
                user_rep = UserRepository(session)
                private_chat_rep = PrivateChatRepository(session)
                message_rep = MessageRepository(session)

                other_user = await user_rep.get_by_id(to_user_id)
                if not other_user:
                    await websocket.send_text(json.dumps({"error": "user not found"}))
                    continue

                private_chat = await private_chat_rep.get_by_users(current_user, other_user)
                if not private_chat:
                    private_chat = await private_chat_rep.create(current_user, other_user)

                await message_rep.create(private_chat.id_, current_user.id_, content)

            await connection_manager.send_to(
                to_user_id,
                json.dumps({"from_user_id": current_user.id_, "content": content})
            )
    finally:
        connection_manager.disconnect(current_user.id_)
