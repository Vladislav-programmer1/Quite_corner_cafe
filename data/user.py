from datetime import datetime as dt
from typing import Literal

import sqlalchemy as sa
from flask_login import UserMixin
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash, generate_password_hash

SqlAlchemyBase: DeclarativeMeta = declarative_base()


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String)
    surname = sa.Column(sa.String)
    sex = sa.Column(sa.String)
    phone_number = sa.Column(sa.String)
    email = sa.Column(sa.String, unique=True, index=True)
    level_of_loyalty = sa.Column(sa.Integer, default=0)
    hashed_password = sa.Column(sa.String)
    order = sa.Column(sa.Integer, sa.ForeignKey('orders.id'), nullable=True)
    creation_datetime = sa.Column(sa.DateTime, default=dt.now)
    modified_datetime = sa.Column(sa.DateTime, default=dt.now, nullable=True)
    user_level = sa.Column(sa.Integer, default=1)
    orders = relationship('Order', lazy='selectin')

    def __init__(self, *, name: str,
                 surname: str,
                 sex: Literal['M', 'F', 'М', 'Ж'],
                 phone_number: str,
                 email: str,
                 password: str
                 ):
        self.name = name
        self.surname = surname
        self.sex = sex
        self.phone_number = phone_number
        self.email = email
        self.set_password(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.hashed_password, password)

    def set_password(self, password: str) -> None:
        self.hashed_password = self.get_hash(password)

    @staticmethod
    def get_hash(value: str):
        return generate_password_hash(value)
