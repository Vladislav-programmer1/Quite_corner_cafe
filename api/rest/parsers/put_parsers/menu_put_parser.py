from flask_restful.reqparse import RequestParser

menu_put_parser = RequestParser()
menu_put_parser.add_argument('id', required=False, type=int)
menu_put_parser.add_argument('dish_name', required=False, type=str)
menu_put_parser.add_argument('category', required=False, type=str)
menu_put_parser.add_argument('img_src', required=False, type=str)
menu_put_parser.add_argument('description', required=False, type=str)
menu_put_parser.add_argument('price', required=False, type=float)
menu_put_parser.add_argument('is_available', required=False, type=bool)
