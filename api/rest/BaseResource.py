import asyncio
import sqlite3
from typing import Any, Optional, Type, Callable

import sqlalchemy
from flask import jsonify
from flask_restful import Resource, abort
from flask_restful.reqparse import RequestParser, Namespace
from sqlalchemy import select
from data import create_session, Order, Menu, User


class BaseResourceList(Resource):
    def __init__(self, post_parser: RequestParser, base: Optional[Type[User | Menu | Order]], name: str,
                 only: tuple[str, ...] = tuple()):
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

    async def validations(self, args):
        ...

    @staticmethod
    def refactor_args(args: Namespace) -> tuple[Namespace, list]:
        return args, list()

    async def _post(self):
        args = self.post_parser.parse_args()
        if (res := await self.validations(args)) is not None:
            return res
        args, action_list = self.refactor_args(args)
        base = self.base_class(**args)
        for action in action_list:
            action(base)
        async with create_session() as session:
            try:
                session.add(base)
                await session.commit()
            except (sqlalchemy.exc.IntegrityError, sqlite3.IntegrityError):
                del base

                return jsonify({'error': 'This object has already exists'})
        return jsonify({'status': 'ok'})

    # @staticmethod
    # def set_values(base, args):
    #     for key, value in args.items():
    #         setattr(base, key, value)


class BaseResourceItem(Resource):
    def __init__(self, put_parser: RequestParser, base, only: tuple[str, ...] = tuple()):
        self.only = only
        self.base: Type[Optional[User | Menu | Order]] = base
        self.put_parser = put_parser

    def get(self, id_: int):
        return asyncio.run(self._get(id_))

    async def _get_item(self, id_: int):
        await abort_if_not_found(id_, self.base)
        async with create_session() as session:
            expression: Any = self.base.id == id_
            item = (await session.execute(select(self.base).where(expression))).first()[0]
        return item

    async def _get(self, id_: int):
        item = await self._get_item(id_)
        return item.to_dict(only=self.only)

    def delete(self, id_: int):
        return asyncio.run(self._delete(id_))

    async def _delete(self, id_: int):
        await abort_if_not_found(id_, self.base)
        async with create_session() as session:
            expression = self.base.id == id_
            user = (await (session.execute(select(self.base).where(expression)))).first()[0]
            await session.delete(user)
            await session.commit()
        return jsonify({id_: 'deleted'})

    @staticmethod
    def refactor_args(args: Namespace) -> tuple[Namespace, list[Callable]]:
        return args, list()

    async def validations(self, args: Namespace):
        ...

    async def _put(self, id_: int):
        await abort_if_not_found(id_, self.base)
        args = self.put_parser.parse_args()
        if (res := await self.validations(args)) is not None:
            return res
        args, action_list = self.refactor_args(args)
        base = self.base(**args)
        base.id = id_
        for action in action_list:
            action(base)
        item: User | Order | Menu = await self._get_item(id_)
        for attribute in base.attributes:
            if (value := getattr(base, attribute)) is not None:
                setattr(item, attribute, value)
        async with create_session() as session:
            try:
                await session.merge(item)
                await session.commit()
                return jsonify({id_: 'updated'})
            except Exception as e:
                if e:
                    pass
                return jsonify({"error": e.args})

    def put(self, id_: int):
        return asyncio.run(self._put(id_))

    # TODO: api_key verification


async def abort_if_not_found(id_, class_):
    async with create_session() as session:
        expression: Any = class_.id == id_
        obj = (await session.execute(select(class_).where(expression))).first()
        if not obj:
            abort(404, message=f"Data with id {id_} is  not found")
