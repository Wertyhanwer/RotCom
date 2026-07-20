from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

from db.configs.engine_config import ip, user, password, port, dbname
import asyncio

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

from db.models.user import User
from db.models.private_chat import PrivateChat
from db.models.message import Message

from db.models.base import Base
target_metadata = Base.metadata



# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:

    def do_run_migrations(connection):
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

    engine = create_async_engine(
        url=f"postgresql+asyncpg://{user}:{password}@{ip}:{port}/{dbname}",
        echo=True
    )
    async with engine.begin() as conn:
       await conn.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
