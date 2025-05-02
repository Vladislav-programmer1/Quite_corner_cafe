import asyncio

import sqlalchemy
from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy import select

from data import create_session


class BaseResourceList(Resource):
    def __init__(self, put_parser: RequestParser, post_parser: RequestParser, base, name, only=tuple()):
        self.put_parser = put_parser
        self.post_parser = post_parser
        self.base_class = base
        self.only = only
        self.name = name

    def get(self):
        return asyncio.run(self._get())

    async def _get(self):
        async with create_session() as session:
            data = map(lambda x: x[0], (await session.execute(select(self.base_class))).all())
        return jsonify({self.name: [item.to_dict(
            only=self.only) for item
            in
            data]})

    def post(self):
        return asyncio.run(self._post())

    def validations(self, args):
        pass

    async def _post(self):
        args = self.post_parser.parse_args()
        self.validations(args)
        base = self.base_class()
        base.id = args['id']
        base.name = args['name']
        base.surname = args['surname']
        base.sex = args['sex']
        base.email = args['email']
        base.phone_number = args['phone_number']
        base.set_password(args['password'])
        if order := args['order']:
            base.order = order
        base.level_of_loyalty = args['level_of_loyalty']
        async with create_session() as session:
            try:
                session.add(base)
                await session.commit()
            except sqlalchemy.exc.IntegrityError:
                del base
                return jsonify({'error': 'This already is already set for other user. Email must be unique.'})
        return jsonify({'status': 'ok'})

# TODO: base-resource for DRY principe
