import asyncio
from typing import Any

import sqlalchemy
from flask import jsonify
from flask_restful import Resource, abort
from sqlalchemy import select

from api.email_validation_api.email_validation import validate_email
from api.phone_number_validation_api import validate_phone_number
from api.rest.parsers import parser
from data import create_session, User


class ListUsers(Resource):
    def get(self):
        return asyncio.run(self._get())

    @staticmethod
    async def _get():
        async with create_session() as session:
            users = map(lambda x: x[0], (await session.execute(select(User))).all())
        return jsonify({'users': [user.to_dict(
            only=('id', 'name', 'surname', 'email',
                  'phone_number', 'sex', 'level_of_loyalty', 'creation_datetime', 'user_level')) for user
            in
            users]})

    def post(self):
        return asyncio.run(self._post())

    @staticmethod
    async def _post():
        args = parser.parse_args()
        if not validate_email(email := args['email']):
            return jsonify({'error': 'Invalid email'})
        if not validate_phone_number(phone_number := args['phone_number']):
            return jsonify({'error': 'Invalid phone number'})
        if any(not args[value].isalpha() for value in ('name', 'surname', 'sex')):
            return jsonify({'error': 'Name, surname and sex must be strings'})
        user = User()
        user.id = args['id']
        user.name = args['name']
        user.surname = args['surname']
        user.sex = args['sex']
        user.email = email
        user.phone_number = phone_number
        user.set_password(args['password'])
        if order := args['order']:
            user.order = order
        user.level_of_loyalty = args['level_of_loyalty']
        async with create_session() as session:
            try:
                session.add(user)
                await session.commit()
            except sqlalchemy.exc.IntegrityError:
                del user
                return jsonify({'error': 'This already is already set for other user. Email must be unique.'})
        return jsonify({'status': 'ok'})


class UserItem(Resource):

    def get(self, user_id: int):
        return asyncio.run(self._get(user_id))

    @staticmethod
    async def _get(user_id: int):
        await abort_if_not_found(user_id, User)
        async with create_session() as session:
            expression: Any = User.id == user_id
            user = (await session.execute(select(User).where(expression))).first()[0]
        return user.to_dict(
            only=('id', 'name', 'surname', 'email', 'level_of_loyalty', 'creation_datetime', 'user_level'))

    def delete(self, user_id: int):
        return asyncio.run(self._delete(user_id=user_id))

    @staticmethod
    async def _delete(user_id: int):
        await abort_if_not_found(user_id, User)
        async with create_session() as session:
            expression = User.id == user_id
            user = (await (session.execute(select(User).where(expression)))).first()[0]
            await session.delete(user)
            await session.commit()
        return jsonify({user_id: 'deleted'})

    @staticmethod
    def put(user_id: int):
        abort_if_not_found(user_id, User)
        pass


async def abort_if_not_found(id_, class_):
    async with create_session() as session:
        expression: Any = class_.id == id_
        obj = (await session.execute(select(class_).where(expression))).first()
        if not obj:
            abort(404, message=f"Data with id {id_} is  not found")
