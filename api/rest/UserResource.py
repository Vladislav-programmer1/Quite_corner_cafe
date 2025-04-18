import sqlalchemy
from flask import jsonify
from flask_restful import Resource, abort

from api.email_validation_api.email_validation import validate_email
from api.rest.parsers import parser
from data import create_session, User


class ListUsers(Resource):
    @staticmethod
    def get():
        with create_session() as session:
            users: list = session.query(User).all()
        return jsonify(
            {'users': [user.to_dict(
                only=('id', 'name', 'surname', 'email', 'level_of_loyalty', 'creation_datetime', 'user_level'))
                for user in users]})

    @staticmethod
    def post():
        args = parser.parse_args()
        user = User()
        user.id = args['id']
        user.name = args['name']
        user.surname = args['surname']
        user.hashed_password = args['hashed_password']
        if validate_email(args['email']):
            user.email = args['email']
        else:
            del user
            return jsonify({'error': 'Invalid email'})
        user.level_of_loyalty = args['level_of_loyalty']
        with create_session() as session:
            try:
                session.add(user)
                session.commit()
            except sqlalchemy.exc.IntegrityError:
                del user
                return jsonify({'error': 'This already is already set for other user. Email must be unique.'})
        return jsonify({'status': 'ok'})


class UserItem(Resource):

    @staticmethod
    def get(user_id: int):
        abort_if_not_found(user_id, User)
        with create_session() as session:
            user: User = session.query(User).get(user_id)
        return user.to_dict(
            only=('id', 'name', 'surname', 'email', 'level_of_loyalty', 'creation_datetime', 'user_level'))

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
        abort_if_not_found(user_id, User)
        pass


def abort_if_not_found(id_, class_):
    with create_session() as session:
        obj = session.query(class_).get(id_)
        if not obj:
            abort(404, message=f"Data with id {id_} is  not found")
