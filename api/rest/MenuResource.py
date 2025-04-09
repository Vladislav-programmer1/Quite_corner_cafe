from flask import jsonify
from flask_restful import Resource


class Menu(Resource):
    @staticmethod
    def get():
        return jsonify({'check': 'success'})