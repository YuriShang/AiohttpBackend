from datetime import datetime
from json.decoder import JSONDecodeError

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import create_async_engine

from app.settings import config
from app.my_test_app.db.models import users, user_privileges

DATABASE_URL = config["postgres"]["database_url"]

engine = create_async_engine(DATABASE_URL, future=True, echo=False)


async def login(username):
    """
    Логинимся в систему
    Функция возвращает словарь с данными пользователя
    """
    login_data = {"login": '', "password": '', "privileges": '', "blocked": False}

    async with engine.begin() as conn:
        result = await conn.execute(
            select(users.c.login, users.c.password).where(users.c.login == username))
        privileges = await conn.execute(
            select(user_privileges.c.privileges,
                   user_privileges.c.block).where(user_privileges.c.login == username))

        for k, v in zip(login_data, list(*result) + list(*privileges)):
            login_data[k] = v

        return login_data


async def get_user(username):
    """
    Возвращаем пользователя из БД по лоигну
    """
    async with engine.begin() as conn:
        user = await conn.execute(select(users.c.login).where(users.c.login == username))
    return user.fetchall()


async def read_users():
    """
    Возвращает список пользователей
    Необходимо изменить функционал, чтобы пароль мог видеть только админ.
    В данной реализации любой пользователь имеет доступ к информации пользователей.
    """
    user_data = {"login": '', "name": '', "surname": '', "password": '', "birthday": ''}
    async with engine.connect() as conn:
        result = await conn.execute(select(users).order_by(users.c.login))
        raw_data = result.fetchall()
        response = ''
        for user in raw_data:
            temp = ''
            for field, data in zip(user_data, user):
                if field == "birthday":
                    data = "{:%B %d, %Y}".format(data)
                user_data[field] = data
                temp += str(f"{field}: {data}, ")
            temp = temp.strip(', ')
            response += temp + '\n'
        return response


async def create_user(request):
    """
    Создаем нового пользователя
    """
    try:  # Проверяем JSON на валидность
        if isinstance(request, dict):
            request_json = request
        else:
            request_json = await request.json()
    except JSONDecodeError as err:
        return f"{err.msg}: line {err.lineno} column {err.colno} (char {err.pos})"

    async with engine.begin() as conn:
        try:
            await conn.execute(
                users.insert(),
                [{k: datetime(*map(int, reversed(v.split("."))))
                    if k == "birthday"
                    else v for k, v in request_json.items()}]
            )

            await conn.execute(
                user_privileges.insert(), [{"login": request_json["login"],
                                            "privileges": request_json["privileges"]}]
            )
        except Exception as err:
            print(err)
            return str(err)
    return f"User with login '{request_json['login']}' successfully created"


async def update_user(request):
    """
    Обновляем данные пользователя
    """
    try:  # Проверяем JSON на валидность
        request_json = await request.json()
    except JSONDecodeError as err:
        return f"{err.msg}: line {err.lineno} column {err.colno} (char {err.pos})"

    async with engine.begin() as conn:
        await conn.execute(
            users.update(users.c.login == request_json["login"]),
            [{k: datetime(*map(int, reversed(v.split("."))))
                if k == "birthday"
                else v for k, v in request_json.items()}]
        )
        await conn.execute(
            user_privileges.update(user_privileges.c.login == request_json["login"]),
            [{"login": request_json["login"],
              "privileges": request_json["privileges"], }]
        )
        if request_json.get("block", None):
            await conn.execute(
                user_privileges.update(user_privileges.c.login == request_json["login"]), [{"block": True}]
            )

    return f"Data of user '{request_json['login']}' was successfully updated!"


async def delete_user(request):
    """
    Удаляем пользователя по лоигну
    """
    try:  # Проверяем JSON на валидность
        request_json = await request.json()
    except JSONDecodeError as err:
        return f"{err.msg}: line {err.lineno} column {err.colno} (char {err.pos})"

    async with engine.begin() as conn:
        await conn.execute(
            users.delete(users.c.login == request_json["login"])
        )
        return f"User '{request_json['login']}' was successfully removed!"


async def block_user(request):
    """
    Баним пользователя
    """
    try:  # Проверяем JSON на валидность
        request_json = await request.json()
    except JSONDecodeError as err:
        return f"{err.msg}: line {err.lineno} column {err.colno} (char {err.pos})"
    async with engine.begin() as conn:
        await conn.execute(
            user_privileges.update(user_privileges.c.login == request_json["login"]), [{"block": True}]
        )
    return f"User '{request_json['login']}' was successfully BANNED!"


async def unblock_user(request):
    """
    Освобождаем пользователя от мук бана
    """
    request_json = await request.json()
    async with engine.begin() as conn:
        await conn.execute(
            user_privileges.update(user_privileges.c.login == request_json["login"]), [{"block": False}]
        )
    return f"User '{request_json['login']}' was successfully undanned!"
