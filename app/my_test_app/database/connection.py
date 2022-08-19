import contextlib
from sqlalchemy.ext.asyncio import create_async_engine
from app.settings import config

engine = create_async_engine(config["postgres"]["database_url"], echo=False, future=True)


async def get_connection():
    connection = None

    @contextlib.asynccontextmanager
    async def connect():
        nonlocal connection

        if connection is None:
            async with engine.connect() as connection:
                yield connection
        else:
            yield connection

    return connect
