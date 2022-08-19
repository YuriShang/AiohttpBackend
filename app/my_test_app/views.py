from aiohttp import web

from aiohttp_auth import auth
from aiohttp_auth.auth import auth_required
from aiohttp_auth.autz import autz_required

from app.my_test_app.database.handlers import read_users, create_user, update_user, \
                                           delete_user, login, block_user, unblock_user

from app.my_test_app.database.connection import get_connection


def index_handler(request):
    return web.Response(
        text='<h1>Hello!</h1>',
        content_type='text/html')


async def log_in(request):
    params = await request.post()
    user = params.get('username', None)
    password = params.get('password', None)
    user_data = await login(user, await get_connection())

    if user == user_data["login"] and password == user_data['password']:
        await auth.remember(request, user)
        return web.Response(text=f"User '{user}' was logged in!")

    return web.Response(text='Wrong username or password',
                        status=401)


@auth_required
async def log_out(request):
    await auth.forget(request)
    return web.Response(text=f"User '{await auth.get_auth(request)}' was logged out!")


@autz_required('read')
async def read(request):
    current_username = await auth.get_auth(request)  # для проверки на админа
    users = await read_users(await get_connection(), current_username)
    return web.Response(text=users, content_type="application/json")


@autz_required('create')
async def create(request):
    text = await create_user(request, await get_connection())
    return web.Response(
        text=text, content_type="application/json",
    )


@autz_required('update')
async def update(request):
    response = await update_user(request, await get_connection())
    return web.Response(text=response)


@autz_required('delete')
async def delete(request):
    response = await delete_user(request, await get_connection())
    return web.Response(text=response)


@autz_required('block')
async def block(request):
    response = await block_user(request, await get_connection())
    return web.Response(text=response)


@autz_required('unblock')
async def unblock(request):
    response = await unblock_user(request, await get_connection())
    return web.Response(text=response)
