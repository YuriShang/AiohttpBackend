from sqlalchemy import Table, Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy import MetaData

metadata_obj = MetaData()

users = Table('users', metadata_obj,
              Column('login', String, unique=True, primary_key=True),
              Column('name', String, nullable=False),
              Column('surname', String),
              Column('password', String, nullable=False),
              Column('birthday', DateTime, nullable=False),
              )

user_privileges = Table('user_privileges', metadata_obj,
                        Column('login', String,  ForeignKey("users.login", ondelete="CASCADE"), primary_key=True),
                        Column('privilege', String, nullable=False),
                        Column('block', Boolean, default=False, nullable=False),
                        )
