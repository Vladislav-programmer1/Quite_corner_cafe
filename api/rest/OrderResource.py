from api import BaseResourceList, BaseResourceItem
from api.rest import order_parser
from data import Order


class OrderList(BaseResourceList):
    def __init__(self):
        super().__init__(order_parser, Order, 'orders',
                         only=('id', 'position_list', 'count_list', 'price', 'is_payed', 'yet_to_cook'))


class OrderItem(BaseResourceItem):
    def __init__(self):
        super().__init__(order_parser, Order, ('id', 'position_list', 'count_list', 'price', 'is_payed', 'yet_to_cook'))
