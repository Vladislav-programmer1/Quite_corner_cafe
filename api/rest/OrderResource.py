from flask_restful import Resource


class OrderList(Resource):
    @staticmethod
    def get():
        pass

    @staticmethod
    def post():
        pass


class OrderItem(Resource):

    @staticmethod
    def get(order_id: int):
        pass

    @staticmethod
    def put(order_id: int):
        pass

    @staticmethod
    def delete(order_id: int):
        pass
