from flask_restful.reqparse import RequestParser

parser = RequestParser()
parser.add_argument('id', required=False, type=int)
parser.add_argument('name', required=True, type=str)
parser.add_argument('surname', required=True, type=str)
parser.add_argument('email', required=True, type=str)
parser.add_argument('level_of_loyalty', required=False, type=int)
parser.add_argument('hashed_password', required=True, type=str)


