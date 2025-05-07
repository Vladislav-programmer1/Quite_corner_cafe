from flask_restful.reqparse import RequestParser

order_parser = RequestParser()
order_parser.add_argument('id', required=False, type=int)
order_parser.add_argument('order_time', required=False, type=str)
order_parser.add_argument('target_time', required=True, type=str)
order_parser.add_argument('position_list', required=True, type=str)
order_parser.add_argument('count_list', required=False, type=str)
order_parser.add_argument('price', required=True, type=float)
order_parser.add_argument('yet_to_cook', required=False, type=bool)
order_parser.add_argument('is_payed', required=False, type=bool)
