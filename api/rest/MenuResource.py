from flask import jsonify
from sqlalchemy import select

from api.rest.parsers import menu_parser, menu_put_parser
from data import Menu, create_session
from .BaseResource import BaseResourceList, BaseResourceItem


class MenuList(BaseResourceList):

    def __init__(self):
        super().__init__(menu_parser, Menu, 'menu')

    async def _get(self):
        async with create_session() as session:
            data = map(lambda x: x[0], (await session.execute(select(self.base_class))).all())
        res_dict = dict()
        for item in data:
            res_dict[item.category] = res_dict.get(item.category, []) + [item.to_dict()]
        return jsonify({self.name: res_dict})


class MenuItem(BaseResourceItem):
    def __init__(self):
        super().__init__(menu_put_parser, Menu)
