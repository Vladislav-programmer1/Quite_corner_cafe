from flask_restful.reqparse import RequestParser

menu_parser = RequestParser()
menu_parser.add_argument('id', required=False, type=int)
menu_parser.add_argument('dish_name', required=True, type=str)
menu_parser.add_argument('img_src', required=True, type=str)
menu_parser.add_argument('description', required=False, type=str)
menu_parser.add_argument('price', required=True, type=float)
menu_parser.add_argument('is_available', required=False, type=bool)