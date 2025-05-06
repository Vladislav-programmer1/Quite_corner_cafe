from datetime import datetime as dt

from sqlalchemy import Column, Time, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from .user import SqlAlchemyBase


class Order(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_time = Column(Time, default=lambda: dt.now().time())
    target_time = Column(Time)
    position_list = Column(String)
    count_list = Column(String)
    price = Column(Float)
    yet_to_cook = Column(Boolean, default=True)
    is_payed = Column(Boolean, default=False)
    user = relationship('User', back_populates='orders', lazy='selectin')

    def __init__(self, *, order_time: dt.time,
                 target_time: dt.time,
                 position_list: str,
                 count_list: str,
                 price: float,
                 yet_to_cook: bool = True,
                 is_payed: bool = False):
        self.order_time = order_time
        self.target_time = target_time
        self.position_list = position_list
        self.count_list = count_list
        self.price = price
        self.yet_to_cook = yet_to_cook
        self.is_payed = is_payed
