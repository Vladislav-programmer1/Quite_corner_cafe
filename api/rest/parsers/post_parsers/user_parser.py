from flask_restful.reqparse import RequestParser

parser = RequestParser()
parser.add_argument('id', required=False, type=int)
parser.add_argument('name', required=True, type=str)
parser.add_argument('surname', required=True, type=str)
parser.add_argument('sex', required=True, type=str, choices=['М', 'Ж', 'M', 'F', 'Мужской', 'Женский'])
parser.add_argument('email', required=True, type=str)
parser.add_argument('phone_number', required=True, type=str)
parser.add_argument('level_of_loyalty', required=False, type=int)
parser.add_argument('order', required=False, default=None, type=int)
parser.add_argument('password', required=True, type=str)
parser.add_argument('user_level', required=False, default=1, type=int)
