import os
from urllib.parse import quote_plus

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27018")
MONGO_DB = os.getenv("MONGO_DB", "rotcom")
MONGO_USER = os.getenv("MONGO_USER", "rotcom")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "12345")

mongo_url = f"mongodb://{quote_plus(MONGO_USER)}:{quote_plus(MONGO_PASSWORD)}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
mongo_dbname = MONGO_DB
