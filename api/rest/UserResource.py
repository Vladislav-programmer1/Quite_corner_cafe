from flask import jsonify
from flask_restful.reqparse import Namespace

from api.email_validation_api.email_validation import validate_email
from api.phone_number_validation_api import validate_phone_number
from api.rest.BaseResource import BaseResourceList, BaseResourceItem
from api.rest.parsers import parser, put_parser
from data import User


class ListUsers(BaseResourceList):
    def __init__(self):
        super().__init__(parser, User, 'users',
                         ('id', 'name', 'surname', 'email', 'phone_number', 'sex', 'modified_datetime',
                          'level_of_loyalty', 'creation_datetime', 'user_level'))

    async def validations(self, args: Namespace):
        if not await validate_email(args['email']):
            return jsonify({'error': 'Invalid email'})
        if not await validate_phone_number(args['phone_number']):
            return jsonify({'error': 'Invalid phone number'})
        if any(not args[value].isalpha() for value in ('name', 'surname', 'sex')):
            return jsonify({'error': 'Name, surname and sex must be strings'})

    @staticmethod
    def refactor_args(args: Namespace) -> tuple[Namespace, list]:
        res_list = list()
        if 'password' in args.keys():
            password = args['password']
            res_list.append(lambda self: self.set_password(password))
            del args['password']
        return args, res_list


class UserItem(BaseResourceItem):
    def __init__(self):
        super().__init__(put_parser, User,
                         ('id', 'name', 'surname', 'email', 'level_of_loyalty', 'creation_datetime', 'user_level'))

    @staticmethod
    def refactor_args(args: Namespace) -> tuple[Namespace, list]:
        res_list = list()
        if 'password' in args.keys():
            password = args['password']
            res_list.append(lambda self: self.set_password(password))
            del args['password']
        return args, res_list

    async def validations(self, args: Namespace):
        if args.get('email') and not await validate_email(args['email']):
            return jsonify({'error': 'Invalid email'})
        if args.get('phone_number') and not await validate_phone_number(args['phone_number']):
            return jsonify({'error': 'Invalid phone number'})
        for value in ('name', 'surname', 'sex'):
            if args[value] is not None:
                if not args[value].isalpha():
                    return jsonify({'error': 'Name, surname and sex must be strings'})
