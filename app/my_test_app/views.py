from aiohttp import web
from app.my_test_app.db_handlers import read_users, create_user, update_user, delete_user, login, block_user

from aiohttp_auth import auth, autz
from aiohttp_auth.auth import auth_required
from aiohttp_auth.autz import autz_required


@autz_required('view')
def index_handler(request):
    return web.Response(
        text='<h1>Hello!</h1>',
        content_type='text/html')


async def log_in(request):
    params = await request.post()
    user = params.get('username', None)
    password = params.get('password', None)

    user_data = await login(user)

    if user == user_data["login"] and password == user_data['password']:
        # remember user identity
        await auth.remember(request, user)
        return web.Response(text='Ok')

    raise web.HTTPUnauthorized()


@auth_required
async def log_out(request):
    await auth.forget(request)
    return web.Response(text='Ok')


async def read(request):
    users = await read_users()
    return web.Response(text=str(users))


@autz_required('create')
async def create(request):
    text = await create_user(request)
    return web.Response(
        text=text, content_type="application/json",
    )


@autz_required('update')
async def update(request):
    await update_user(request)


@autz_required('delete')
async def delete(request):
    await delete_user(request)


@autz_required('block')
async def block(request):
    await block_user(request)

