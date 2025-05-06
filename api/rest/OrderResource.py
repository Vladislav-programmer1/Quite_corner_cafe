from flask import jsonify

from api.rest import order_parser
from data import Order
from .BaseResource import BaseResourceList, BaseResourceItem


class OrderList(BaseResourceList):
    def __init__(self):
        super().__init__(order_parser, Order, 'orders',
                         only=('id', 'position_list', 'count_list', 'price', 'is_payed', 'yet_to_cook'))

    def validations(self, args):
        try:
            count_list = args['count_list']
            position_list = args['position_list']
            assert len(count_list.split(" ")) == len(position_list.split(" "))
        except AssertionError:
            return jsonify({'error': ''})
        except Exception as e:
            if e:
                pass
            return jsonify({'error': 'Invalid request params'})


class OrderItem(BaseResourceItem):
    def __init__(self):
        super().__init__(order_parser, Order, ('id', 'position_list', 'count_list', 'price', 'is_payed', 'yet_to_cook'))
