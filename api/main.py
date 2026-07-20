from logger.logger_config import setup_logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users_router, registration_router, loging_router, private_chats_router
from ws import ws_chat_router

setup_logging()

app = FastAPI(title="RotCom")
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