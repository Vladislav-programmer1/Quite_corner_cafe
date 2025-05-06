import sqlalchemy as sa
from sqlalchemy_serializer import SerializerMixin

from data.user import SqlAlchemyBase


class Menu(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Menu'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    dish_name = sa.Column(sa.String, index=True, unique=True)
    category = sa.Column(sa.String, index=True)
    description = sa.Column(sa.String, nullable=True)
    img_src = sa.Column(sa.String)

    price = sa.Column(sa.Float)
    is_available = sa.Column(sa.Boolean, default=True)

    def __init__(self, **kwargs):
        self.dish_name = kwargs.get('dish_name') if kwargs.get('dish_name') else self.is_available
        self.category = kwargs.get('category') if kwargs.get('category') else self.is_available
        self.description = kwargs.get('description') if kwargs.get('description') else self.is_available
        self.img_src = kwargs.get('img_src') if kwargs.get('img_src') else self.is_available
        self.price = kwargs.get('price') if kwargs.get('price') else self.is_available
        self.is_available = kwargs.get('is_available') if kwargs.get('is_available') else self.is_available
