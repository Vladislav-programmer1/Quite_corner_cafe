from flask_restful.reqparse import RequestParser

parser = RequestParser()
parser.add_argument('id', required=False, type=int)
parser.add_argument('name', required=True, type=str)
parser.add_argument('surname', required=True, type=str)
parser.add_argument('email', required=True, type=str)
parser.add_argument('level_of_loyalty', required=False, type=int)
parser.add_argument('hashed_password', required=True, type=str)

menu_parser = RequestParser()
menu_parser.add_argument('id', required=False, type=int)
menu_parser.add_argument('dish_name', required=True, type=str)
menu_parser.add_argument('img_src', required=True, type=str)
menu_parser.add_argument('description', required=False, type=str)
menu_parser.add_argument('price', required=True, type=int)
menu_parser.add_argument('is_available', required=False, type=bool)
