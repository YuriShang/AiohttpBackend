import asyncio

from logging.config import fileConfig

from alembic import context
from app.my_test_app.database.models import metadata_obj
from app.my_test_app.database.connection import get_connection


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = metadata_obj


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():

    connection = await get_connection()

    async with connection() as conn:
        await conn.run_sync(do_run_migrations)

asyncio.run(run_migrations_online())
