from aiohttp import web
from aiohttp_auth.autz.policy import acl
from app.my_test_app.db_handlers import login


class ACLAutzPolicy(acl.AbstractACLAutzPolicy):
    def __init__(self, context=None):
        super().__init__(context)

    async def acl_groups(self, user_identity):
        user_data = await login(user_identity)
        privilege = user_data.get("privilege", None)

        if privilege is None:
            # return empty tuple in order to give a chance
            # to Group.Everyone
            return tuple()

        return privilege,


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
