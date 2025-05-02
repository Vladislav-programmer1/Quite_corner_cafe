import asyncio
from typing import Any

from flask import jsonify
from flask_restful import Resource
from sqlalchemy import select

from api.rest.parsers import menu_parser
from data import Menu
from data import create_session
from .UserResource import abort_if_not_found


class MenuList(Resource):
    def get(self):
        return asyncio.run(self._get())

    @staticmethod
    async def _get():
        async with create_session() as session:
            menu_list = map(lambda x: x[0], (await session.execute(select(Menu))).all())
        return {'menu': [menu.to_dict(
        ) for menu
            in
            menu_list]}

    @staticmethod
    async def _post():
        args = menu_parser.parse_args()
        menu = Menu()
        menu.id = args['id']
        menu.img_src = args['img_src']
        menu.dish_name = args['dish_name']
        menu.description = args['description']
        menu.price = args['price']
        menu.is_available = args['is_available']
        try:
            async with create_session() as session:
                session.add(menu)
                await session.commit()
                return jsonify({'success': 'ok'})
        except Exception as e:
            return jsonify({'message': e})

    def post(self):
        return asyncio.run(self._post())


class MenuItem(Resource):
    @staticmethod
    async def _get(item_id: int):
        await abort_if_not_found(item_id, Menu)
        async with create_session() as session:
            expression: Any = Menu.id == item_id
            menu = (await session.execute(select(Menu).where(expression))).first()[0]
        return menu.to_dict()

    def get(self, item_id: int):
        return asyncio.run(self._get(item_id))

    @staticmethod
    async def _delete(item_id: int):
        await abort_if_not_found(item_id, Menu)
        async with create_session() as session:
            expression: Any = Menu.id == item_id
            menu_item = (await session.execute(select(Menu).where(expression))).first()[0]
            await session.delete(menu_item)
            await session.commit()
        return jsonify({item_id: 'deleted'})

    def delete(self, item_id: int):
        return asyncio.run(self._delete(item_id))

    @staticmethod
    def put(item_id: int):
        pass
