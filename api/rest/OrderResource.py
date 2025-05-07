import datetime

from flask import jsonify
from flask_restful.reqparse import Namespace

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

    @staticmethod
    def refactor_args(args: Namespace) -> tuple[Namespace, list]:
        for el in 'order_time', 'target_time':
            if el in args.keys():
                try:
                    hour, minutes = map(int, args[el].split(':'))
                    args[el] = datetime.time(hour=hour, minute=minutes)
                except Exception as e:
                    if e:
                        pass
        return args, list()


class OrderItem(BaseResourceItem):
    def __init__(self):
        super().__init__(order_parser, Order,
                         ('id', 'position_list', 'count_list', 'price', 'is_payed', 'target_time', 'order_time',
                          'yet_to_cook'))

    @staticmethod
    def refactor_args(args: Namespace) -> tuple[Namespace, list]:
        for el in 'order_time', 'target_time':
            if el in args.keys():
                try:
                    hour, minutes = map(int, args[el].split(':'))
                    args[el] = datetime.time(hour=hour, minute=minutes)
                except Exception as e:
                    if e:
                        pass
        return args, list()
