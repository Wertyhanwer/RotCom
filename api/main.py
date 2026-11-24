import asyncio
import os
from contextlib import asynccontextmanager

from logger.logger_config import setup_logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.mongo_engine import MongoEngine
from routers import users_router, registration_router, loging_router, private_chats_router, calls_router, \
    auth_tokens_router
from ws import ws_chat_router
from ws.connection_manager import connection_manager
from dependencies.db import get_session
from services.chat_events import run_reconciler

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo = MongoEngine()
    await mongo.create_indexes()
    await connection_manager.start()
    reconciler = asyncio.create_task(run_reconciler(get_session, mongo.get_db()))
    yield
    reconciler.cancel()
    await connection_manager.stop()
    await mongo.close()


app = FastAPI(title="RotCom", lifespan=lifespan)
# Фронтенд обращается к api через nginx с того же origin (/api), поэтому по умолчанию CORS
# не разрешён никому. Раньше было allow_origins=["*"] вместе с allow_credentials=True: Starlette
# в этом случае отражает любой Origin, и любой сайт мог делать запросы к api из браузера.
# Авторизация идёт заголовком Authorization, а не куками, поэтому credentials не нужны.
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(users_router)
app.include_router(registration_router)
app.include_router(loging_router)
app.include_router(private_chats_router)
app.include_router(ws_chat_router)
app.include_router(calls_router)
app.include_router(auth_tokens_router)