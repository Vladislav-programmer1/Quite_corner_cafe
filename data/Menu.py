import sqlalchemy as sa
from sqlalchemy_serializer import SerializerMixin

from data import SqlAlchemyBase


class Menu(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Menu'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    dish_name = sa.Column(sa.String)
    description = sa.Column(sa.String, nullable=True)
    img_src = sa.Column(sa.String)
    price = sa.Column(sa.Double)
    is_available = sa.Column(sa.Boolean, default=True)


