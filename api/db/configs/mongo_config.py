import os

from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27018")
MONGO_DB = os.getenv("MONGO_DB", "rotcom")
MONGO_USER = os.getenv("MONGO_USER", "rotcom")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
if not MONGO_PASSWORD:
    raise RuntimeError("MONGO_PASSWORD is not set")

mongo_url = f"mongodb://{quote_plus(MONGO_USER)}:{quote_plus(MONGO_PASSWORD)}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
mongo_dbname = MONGO_DB
