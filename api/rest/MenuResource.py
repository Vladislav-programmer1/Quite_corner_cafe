from api.rest.parsers import menu_parser
from data import Menu
from .BaseResource import BaseResourceList, BaseResourceItem


class MenuList(BaseResourceList):

    def __init__(self):
        super().__init__(menu_parser, Menu, 'menu')


class MenuItem(BaseResourceItem):
    def __init__(self):
        super().__init__(menu_parser, Menu)
