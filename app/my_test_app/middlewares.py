from aiohttp import web
from pydantic import BaseModel
from aiohttp_pydantic import PydanticView
from app.my_test_app.db_handlers import login
from aiohttp_basicauth import BasicAuthMiddleware


@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        if response.status != 404:
            return response
        message = response.message
    except web.HTTPException as ex:
        if ex.status != 404:
            raise
        message = ex.reason
    return web.json_response({'error': message})