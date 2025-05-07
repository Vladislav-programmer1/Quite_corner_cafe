import sqlalchemy as sa
from sqlalchemy_serializer import SerializerMixin

from data.user import SqlAlchemyBase
from .BaseModel import BaseModelClass


class Menu(BaseModelClass, SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Menu'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    dish_name = sa.Column(sa.String, index=True, unique=True)
    category = sa.Column(sa.String, index=True)
    description = sa.Column(sa.String, nullable=True)
    img_src = sa.Column(sa.String)

    price = sa.Column(sa.Float)
    is_available = sa.Column(sa.Boolean, default=True)
    __attributes = ('dish_name', 'category', 'description', 'img_src', 'price', 'is_available')

    @property
    def attributes(self):
        return self.__attributes
