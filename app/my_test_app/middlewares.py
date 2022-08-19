from aiohttp import web

from json import JSONDecodeError


@web.middleware
async def json_handler(request, handler):
    """
    Проверяем входящий JSON на валидность
    """
    if request.path in "/login/read/logout":
        return await handler(request)
    elif request.path in "/create/update/block/unblock/delete":
        try:
            await request.json()
            return await handler(request)
        except JSONDecodeError as err:
            message = f"{err.msg}: line {err.lineno} column {err.colno} (char {err.pos})"
            return web.json_response({'error': message})
    else:
        return web.Response(text="404: Not Found", status=404)

