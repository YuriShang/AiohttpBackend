from aiohttp import web
from app.my_test_app.db_handlers import read_users, create_user, update_user, delete_user, login, block_user


def index_handler(request):
    return web.Response(
        text='<h1>Hello!</h1>',
        content_type='text/html')


async def log_in(request):
    pass


async def read(request):
    await read_users()


async def create(request):
    text = await create_user(request)
    return web.Response(
        text=text, content_type="application/json",
    )


async def update(request):
    await update_user(request)


async def delete(request):
    await delete_user(request)


async def block(request):
    await block_user(request)

