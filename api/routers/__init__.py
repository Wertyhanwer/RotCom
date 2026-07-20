from .users import router as users_router
from .auth.login import router as loging_router
from .auth.registration import router as registration_router
from .chats.private_chat import router as private_chats_router

__all__ = [users_router, loging_router, registration_router, private_chats_router]