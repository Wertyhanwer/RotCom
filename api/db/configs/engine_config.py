import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL

# при локальном запуске подхватываем .env из корня репозитория; в docker переменные
# приходят через env_file, а уже заданные переменные окружения load_dotenv не перезаписывает
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "rotcom")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD")
if not DB_PASSWORD:
    raise RuntimeError("DB_PASSWORD is not set")

# echo=True печатает каждый SQL-запрос с параметрами — только для отладки
DB_ECHO = os.getenv("DB_ECHO", "false").lower() in ("1", "true", "yes")


# URL.create сам экранирует спецсимволы в пароле (@, :, / и т.п.), которые ломали f-строку
db_url = URL.create(
    drivername="postgresql+asyncpg",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)
