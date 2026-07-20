
from db.engine import DBEngine

async def get_session_async():
    engine = DBEngine()
    async with engine.get_session() as session:
        yield session

def get_session():
    return DBEngine().get_session()