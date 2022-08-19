from datetime import datetime
from sqlalchemy import Table, Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy import MetaData


# Метаданные для alembic
metadata_obj = MetaData()


# Модель пользователя
users = Table('users', metadata_obj,
              Column('login', String, unique=True, primary_key=True),
              Column('name', String, nullable=False),
              Column('surname', String),
              Column('password', String, nullable=False),
              Column('birthday', DateTime, nullable=False),
              )


# Модель привилегий
user_privileges = Table('user_privileges', metadata_obj,
                        Column('login', String,  ForeignKey("users.login", ondelete="CASCADE"), primary_key=True),
                        Column('privileges', String, nullable=False),
                        Column('block', Boolean, default=False, nullable=False),
                        )


# Учетка админа, создается при развертывании приложения
admin_user = {
    "login": "admin",
    "name": "admin",
    "password": "admin",
    "birthday": datetime(1970, 1, 1),
    "privileges": "admin",
    "block": False
}
