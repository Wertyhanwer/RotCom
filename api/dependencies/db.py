
from db.engine import DBEngine
from db.mongo_engine import MongoEngine

async def get_session_async():
    engine = DBEngine()
    async with engine.get_session() as session:
        yield session

def get_session():
    return DBEngine().get_session()

def get_mongo_db():
    return MongoEngine().get_db()