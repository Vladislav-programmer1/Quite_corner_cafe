from flask_restful.reqparse import RequestParser

put_parser = RequestParser()
put_parser.add_argument('id', required=False, type=int)
put_parser.add_argument('name', required=False, type=str)
put_parser.add_argument('surname', required=False, type=str)
put_parser.add_argument('sex', required=False, type=str, choices=['М', 'Ж', 'M', 'F'])
put_parser.add_argument('email', required=False, type=str)
put_parser.add_argument('phone_number', required=False, type=str)
put_parser.add_argument('level_of_loyalty', required=False, type=int)
put_parser.add_argument('order', required=False, default=False, type=int)
put_parser.add_argument('password', required=False, type=str)
