from flask import jsonify

from api.email_validation_api.email_validation import validate_email
from api.phone_number_validation_api import validate_phone_number
from api.rest.BaseResource import BaseResourceList, BaseResourceItem
from api.rest.parsers import parser,put_parser
from data import User


class ListUsers(BaseResourceList):
    def __init__(self):
        super().__init__(parser, User, 'users',
                         ('id', 'name', 'surname', 'email', 'level_of_loyalty', 'creation_datetime', 'user_level'))

    def validations(self, args):
        if not validate_email(args['email']):
            return jsonify({'error': 'Invalid email'})  # fixme can't start new event loop
        if not validate_phone_number(args['phone_number']):
            return jsonify({'error': 'Invalid phone number'})
        if any(not args[value].isalpha() for value in ('name', 'surname', 'sex')):
            return jsonify({'error': 'Name, surname and sex must be strings'})

    # @staticmethod
    # def set_values(base, args):
    #     BaseResourceList.set_values(base, args)
    #     base.set_password(args['password'])
    #     delattr(base, 'password')
    #


class UserItem(BaseResourceItem):
    def __init__(self):
        super().__init__(put_parser, User,
                         ('id', 'name', 'surname', 'email', 'level_of_loyalty', 'creation_datetime', 'user_level'))
