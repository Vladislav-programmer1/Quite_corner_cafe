from datetime import datetime as dt

from sqlalchemy import Column, Time, Integer, String, Double, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from .user import SqlAlchemyBase


class Order(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_time = Column(Time, default=lambda: dt.now().time())
    position_list = Column(String)
    count_list = Column(String)
    price = Column(Double)
    yet_to_cook = Column(Boolean, default=True)
    is_payed = Column(Boolean, default=False)
    user = relationship('User', back_populates='orders')