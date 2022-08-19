import asyncio
from aiohttp import web
from os import urandom
import aiohttp_auth

from app.settings import config
from app.my_test_app.routes import setup_routes as setup_app_routes
from app.my_test_app.middlewares import json_handler
from app.my_test_app.permissions.permissions import ACLAutzPolicy, context


def setup_routes(application):
    setup_app_routes(application)


# Настраиваем приложение
def setup_app(application):
    setup_routes(application)


# Инициализируем приложение
def init_app(loop):
    app = web.Application(middlewares=[json_handler])

    # Create an auth ticket mechanism that expires after 10 minutes (600
    # seconds), and has a randomly generated secret. Also includes the
    # optional inclusion of the users IP address in the hash
    auth_policy = aiohttp_auth.auth.CookieTktAuthentication(urandom(32), 600, include_ip=True)

    # Create an ACL authorization policy
    autz_policy = ACLAutzPolicy(context=context)

    # setup middlewares in aiohttp fashion
    aiohttp_auth.setup(app, auth_policy, autz_policy)

    return app


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = init_app(loop)
    setup_app(app)

    # Запускаем сервер
    web.run_app(app, port=config["common"]["port"], loop=loop)