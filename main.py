from aiohttp import web
from random import randint

from app.settings import config
from app.my_test_app.routes import setup_routes as setup_app_routes
from app.my_test_app.middlewares import error_middleware


def setup_routes(application):
    setup_app_routes(application)


def setup_config(application):
    application["config"] = config


def setup_app(application):
    setup_config(application)
    setup_routes(application)


app = web.Application(middlewares=[])


if __name__ == "__main__":
    setup_app(app)
    web.run_app(app, port=config["common"]["port"])