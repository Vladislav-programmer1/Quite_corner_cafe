from flask import jsonify
from flask_restful import Resource

from data import Menu
from data import create_session
from .UserResource import abort_if_not_found
from .parser import menu_parser


class MenuList(Resource):
    @staticmethod
    def get():
        with create_session() as session:
            menu: list = session.query(Menu).all()
        return jsonify({'menu': [menu_.to_dict() for menu_ in menu]})

    @staticmethod
    def post():
        args = menu_parser.parse_args()
        menu = Menu()
        menu.id = args['id']
        menu.img_src = args['img_src']
        menu.dish_name = args['dish_name']
        menu.description = args['description']
        menu.price = args['price']
        menu.is_available = args['is_available']
        with create_session() as session:
            session.add(menu)
            session.commit()
        return jsonify({'success': 'ok'})


class MenuItem(Resource):
    @staticmethod
    def get(item_id: int):
        abort_if_not_found(item_id, Menu)
        with create_session() as session:
            return session.query(Menu).get(item_id).to_dict()

    @staticmethod
    def delete(item_id: int):
        abort_if_not_found(item_id, Menu)
        with create_session() as session:
            menu_item = session.query(Menu).get(item_id)
            session.delete(menu_item)
            session.commit()
        return jsonify({item_id: 'deleted'})

    @staticmethod
    def put(item_id: int):
        pass
