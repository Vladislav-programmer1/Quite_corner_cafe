import asyncio

from flask import jsonify
from flask_restful import Resource
from sqlalchemy import select

from data import create_session, Order


class OrderList(Resource):

    def get(self):
        return asyncio.run(self._get())

    @staticmethod
    async def _get():
        async with create_session() as session:
            orders = map(lambda x: x[0], (await session.execute(select(Order))).all())
        return jsonify({'orders': [order.to_dict() for order in orders]})

    def post(self):
        return asyncio.run(self.post())

    @staticmethod
    async def _post():
        pass


class OrderItem(Resource):

    def get(self, order_id: int):
        pass

    def put(self, order_id: int):
        pass

    def delete(self, order_id: int):
        pass
# TODO: rest-api resource for orders
