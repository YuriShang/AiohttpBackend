import asyncio
import json
from datetime import datetime

import sqlalchemy
from sqlalchemy import union
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, joinedload, selectinload

from app.settings import config
from app.my_test_app.models import users, user_privileges

DATABASE_URL = config["postgres"]["database_url"]

engine = create_async_engine(DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def login(request, username, password):
    login_data = {"login": '', "password": '', "privilege": '', "blocked": False}

    async with engine.begin() as conn:
        result = await conn.execute(
            select(users.c.login, users.c.password).where(users.c.login == username))
        privilege = await conn.execute(
            select(user_privileges.c.privilege,
                   user_privileges.c.block).where(user_privileges.c.login == username))

        for k, v in zip(login_data, list(*result) + list(*privilege)):
            login_data[k] = v

        return login_data


async def read_users():
    async with engine.connect() as conn:
        result = await conn.execute(select(users).order_by(users.c.login))
        return result.fetchall()


async def create_user(request):
    request_json = await request.json()
    async with engine.begin() as conn:
        try:
            await conn.execute(
                users.insert(),
                [{k: datetime(*map(int, reversed(v.split("."))))
                    if k == "birthday"
                    else v for k, v in request_json.items() if k != "privileges"}]
            )

            await conn.execute(
                user_privileges.insert(), [{"login": request_json["login"],
                                            "privilege": request_json["privilege"]}]
            )
        except Exception as err:
            return str(err)
    text = f"User with login '{request_json['login']}' successfully created"
    return text


async def update_user(request):
    request_json = await request.json()
    async with engine.begin() as conn:
        await conn.execute(
            users.update(users.c.login == request_json["login"]),
            [{k: datetime(*map(int, reversed(v.split("."))))
                if k == "birthday"
                else v for k, v in request_json.items() if k != "privileges"}]
        )
        await conn.execute(
            user_privileges.update(user_privileges.c.login == request_json["login"]),
            [{"login": request_json["login"],
              "privilege": request_json["privilege"], }]
        )


async def delete_user(request):
    request_json = await request.json()
    async with engine.begin() as conn:
        await conn.execute(
            users.delete(users.c.login == request_json["login"])
        )


async def block_user(request):
    request_json = await request.json()
    async with engine.begin() as conn:
        await conn.execute(
            user_privileges.update(user_privileges.c.login == request_json["login"]), [{"block": True}]
        )
