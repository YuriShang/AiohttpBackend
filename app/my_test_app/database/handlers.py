from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from app.my_test_app.database.models import users, user_privileges


async def login(username, connection):
    """
    Логинимся в систему
    Функция возвращает словарь с данными пользователя
    """
    login_data = {"login": '', "password": '', "privileges": '', "blocked": False}

    async with connection() as conn:
        result = await conn.execute(
            select(users.c.login, users.c.password).where(users.c.login == username))
        privileges = await conn.execute(
            select(user_privileges.c.privileges,
                   user_privileges.c.block).where(user_privileges.c.login == username))

        for k, v in zip(login_data, list(*result) + list(*privileges)):
            login_data[k] = v

        return login_data


async def read_users(connection, username):
    """
    Возвращает список пользователей. Пароль возвращается только в том случае,
    если запрашивающий пользователь обладает правами админа, иначе - 'forbidden'
    """

    async with connection() as conn:
        # Проверяем текущего пользователя на права админа
        permissions = await conn.execute(select(user_privileges.c.privileges).where(user_privileges.c.login == username))
        fetched = permissions.fetchall()

        # запрсшиваем из бд данные пользователя
        users_data = [dict(row._mapping) for row in await conn.execute(select(users).order_by(users.c.login))]
        privileges = [dict(row._mapping) for row in await conn.execute(select(user_privileges))]

        for user, privilege in zip(users_data, privileges):
            user.update(privilege)
            date = user.get("birthday", None)
            if date:
                user["birthday"] = date.strftime("%d.%m.%Y")
            if fetched[0][0] != "admin":
                user["password"] = "forbidden"
        return str(users_data)


async def create_user(request, connection):
    """
    Создаем нового пользователя
    """
    request_json = await request.json()

    async with connection() as conn:
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
            await conn.commit()
        except IntegrityError as err:
            return str(err.orig)
    return f"User with login '{request_json['login']}' successfully created!"


async def update_user(request, connection):
    """
    Обновляем данные пользователя
    """
    request_json = await request.json()

    async with connection() as conn:
        await conn.execute(
            users.update(users.c.login == request_json["login"]),
            [{k: datetime(*map(int, reversed(v.split("."))))
                if k == "birthday"
                else v for k, v in request_json.items()}]
        )
        await conn.execute(
            user_privileges.update(user_privileges.c.login == request_json["login"]),
            [{"login": request_json["login"],
              "privileges": request_json["privileges"]}]
        )
        if request_json.get("block", None):
            await conn.execute(
                user_privileges.update(user_privileges.c.login == request_json["login"]), [{"block": True}]
        )
        await conn.commit()

    return f"Data of user '{request_json['login']}' was successfully updated!"


async def delete_user(request, connection):
    """
    Удаляем пользователя по логину
    """
    request_json = await request.json()

    async with connection() as conn:
        await conn.execute(
            users.delete(users.c.login == request_json["login"])
        )
        await conn.commit()

    return f"User '{request_json['login']}' was successfully removed!"


async def block_user(request, connection):
    """
    Баним пользователя
    """
    request_json = await request.json()

    async with connection() as conn:
        await conn.execute(
            user_privileges.update(user_privileges.c.login == request_json["login"]), [{"block": True}]
        )
        await conn.commit()

    return f"User '{request_json['login']}' was successfully BANNED!"


async def unblock_user(request, connection):
    """
    Освобождаем пользователя от мук бана
    """
    request_json = await request.json()

    async with connection() as conn:
        await conn.execute(
            user_privileges.update(user_privileges.c.login == request_json["login"]), [{"block": False}]
        )
        await conn.commit()

    return f"User '{request_json['login']}' was successfully unbanned!"
