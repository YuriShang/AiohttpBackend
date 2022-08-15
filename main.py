import asyncio
from aiohttp import web
from os import urandom
import aiohttp_auth
from aiohttp_auth.permissions import Permission, Group

from app.settings import config
from app.my_test_app.routes import setup_routes as setup_app_routes
from app.my_test_app.middlewares import error_middleware, ACLAutzPolicy


context = [(Permission.Allow, 'readonly', {'view', }),
           (Permission.Deny, 'readonly', {'edit', }),
           (Permission.Allow, 'admin', {'view', 'create', 'update', 'delete', 'block'}),
           (Permission.Deny, 'block', {'view', 'create', 'update', 'delete', 'block'}),
           (Permission.Allow, Group.Everyone, {'view_home', })]


def setup_routes(application):
    setup_app_routes(application)


def setup_config(application):
    application["config"] = config


def setup_app(application):
    setup_config(application)
    setup_routes(application)


def init_app(loop):
    app = web.Application()

    # Create an auth ticket mechanism that expires after 1 minute (60
    # seconds), and has a randomly generated secret. Also includes the
    # optional inclusion of the users IP address in the hash
    auth_policy = aiohttp_auth.auth.CookieTktAuthentication(urandom(32), 60, include_ip=True)

    # Create an ACL authorization policy
    autz_policy = ACLAutzPolicy(context=context)

    # setup middlewares in aiohttp fashion
    aiohttp_auth.setup(app, auth_policy, autz_policy)

    return app


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = init_app(loop)
    setup_app(app)
    web.run_app(app, port=config["common"]["port"], loop=loop)