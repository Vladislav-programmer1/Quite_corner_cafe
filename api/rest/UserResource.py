from flask import jsonify
from flask_restful import Resource, abort

from data import create_session, User
from .parser import parser


class ListUsers(Resource):
    @staticmethod
    def get():
        with create_session() as session:
            users: list = session.query(User).all()
        return jsonify({'users': [user.to_dict() for user in users]})

    @staticmethod
    def post():
        args = parser.parse_args()
        user = User()
        user.id = args['id']
        user.name = args['name']
        user.surname = args['surname']
        user.hashed_password = args['hashed_password']
        user.email = args['email']
        user.level_of_loyalty = args['level_of_loyalty']
        with create_session() as session:
            session.add(user)
            session.commit()
        # TODO: fix this code. Check email (correct and unique)
        return jsonify({'status': 'ok'})


class UserItem(Resource):
    @staticmethod
    def get(user_id: int):
        abort_if_not_found(user_id, User)
        with create_session() as session:
            user = session.query(User).get(user_id)
        return user.to_dict()

    @staticmethod
    def delete(user_id: int):
        abort_if_not_found(user_id, User)
        with create_session() as session:
            user = session.get(User, user_id)
            session.delete(user)
            session.commit()
        return jsonify({user_id: 'deleted'})

    @staticmethod
    def put(user_id: int):
        pass


def abort_if_not_found(id_, class_):
    with create_session() as session:
        obj = session.query(class_).get(id_)
        if not obj:
            abort(404, message=f"Data with id {id_} is  not found")
