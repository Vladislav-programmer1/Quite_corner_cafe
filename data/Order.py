from datetime import datetime as dt

from sqlalchemy import Column, Time, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship

from .BaseModel import BaseModelClass
from .user import SqlAlchemyBase


class Order(SqlAlchemyBase, BaseModelClass):
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
    __attributes = ('target_time', 'order_time', 'position_list', 'count_list', 'price', 'yet_to_cook', 'is_payed')

    @property
    def attributes(self):
        return self.__attributes
