from flask import jsonify
from flask_restful import Resource


class ListUsers(Resource):
    @staticmethod
    def get():
        return jsonify({'check': 'success'})
