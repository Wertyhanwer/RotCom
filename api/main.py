from contextlib import asynccontextmanager

from logger.logger_config import setup_logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.mongo_engine import MongoEngine
from routers import users_router, registration_router, loging_router, private_chats_router, calls_router
from ws import ws_chat_router

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo = MongoEngine()
    await mongo.create_indexes()
    yield
    await mongo.close()


app = FastAPI(title="RotCom", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users_router)
app.include_router(registration_router)
app.include_router(loging_router)
app.include_router(private_chats_router)
app.include_router(ws_chat_router)
app.include_router(calls_router)