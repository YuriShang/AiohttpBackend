import asyncio
from aiohttp import web
from os import urandom
import aiohttp_auth
from aiohttp_auth.permissions import Permission
from asyncpg.exceptions import UniqueViolationError

from app.settings import config
from app.my_test_app.routes import setup_routes as setup_app_routes
from app.my_test_app.middlewares import ACLAutzPolicy
from app.my_test_app.db.db_handlers import get_user, create_user
from app.my_test_app.db.models import admin_user


context = [
           (Permission.Allow, 'readonly', {'read', }),
           (Permission.Deny, 'readonly', {'create', 'update', 'delete', 'block'}),
           (Permission.Allow, 'admin', {'read', 'create', 'update', 'delete', 'block'}),
           (Permission.Deny, 'block', {'read', 'create', 'update', 'delete', 'block'})\
    ]


def setup_routes(application):
    setup_app_routes(application)


def setup_config(application):
    application["config"] = config


def setup_app(application):
    setup_config(application)
    setup_routes(application)


def init_app(loop):
    app = web.Application()

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

    # Добавляем учетку админа, если она отсутствует
    admin = loop.run_until_complete(get_user("admin"))
    if not admin:
        loop.run_until_complete(create_user(admin_user))
        print("Учетная запись 'admin' с привилегиями 'admin' успешно создана")

    web.run_app(app, port=config["common"]["port"], loop=loop)