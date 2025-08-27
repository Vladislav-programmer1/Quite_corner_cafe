import logging
from os import getenv

from aiohttp import ClientSession, ClientTimeout
from dotenv import load_dotenv

from api import ListUsers, MenuList, MenuItem, UserItem, OrderList, OrderItem
from errors import ApiRequestError

load_dotenv()


class ApiManager:

    def __init__(self, app):
        self.app = app
        self.set_api_resources()
        logging.basicConfig(filename='logs.log',
                            format='%(asctime)s %(levelname)s %(name)s %(message)s',
                            level=logging.WARNING, filemode='w')
        self.logger = logging.getLogger(__name__)

    def set_api_resources(self) -> None:
        """
        Add resources needed to the Api
        :return: None
        """
        self.app.api.add_resource(ListUsers, '/api/v2/users')
        self.app.api.add_resource(MenuList, '/api/v2/menu')
        self.app.api.add_resource(MenuItem, '/api/v2/menu/<int:id_>')
        self.app.api.add_resource(UserItem, '/api/v2/users/<int:id_>')
        self.app.api.add_resource(OrderList, '/api/v2/orders')
        self.app.api.add_resource(OrderItem, '/api/v2/orders/<int:id_>')

    @staticmethod
    async def get_api_list(table: str) -> dict:
        """
        Get menu from api
        :return: json response from api
        """
        async with ClientSession(timeout=ClientTimeout(total=2)) as session_:
            async with session_.get(f'http://{getenv("server")}:{getenv("port")}/api/v2/{table}') as response:
                return await response.json()

    async def post(self, table: str, data: dict) -> bool:
        try:
            async with ClientSession(timeout=ClientTimeout(total=5)) as session:
                async with session.post(f'http://{getenv("server")}:{getenv("port")}/api/v2/{table}',
                                        json=data) as response:
                    match response.status:
                        case 200 | 201:
                            return True
                        case _:
                            raise ApiRequestError(response.status, table)
        except ApiRequestError as e:
            self.logger.error(msg=f'Error while api_post request. Status code: {e.args[0]}. Table:{e.args[1]}')
            return False
        except TimeoutError:
            self.logger.error(msg=f'Time out error')
            return False

    async def put(self, table: str, id_: int, data):
        try:
            async with ClientSession(timeout=ClientTimeout(total=2)) as session:
                async with session.put(f'http://{getenv("server")}:{getenv("port")}/api/v2/{table}/{id_}',
                                       json=data) as response:
                    match response.status:
                        case 200 | 201:
                            return True
                        case _:
                            raise ApiRequestError(response.status, table)
        except ApiRequestError as e:
            self.logger.error(msg=f'Error while api_post request. Status code: {e.args[0]}. Table:{e.args[1]}')
            return False
        except TimeoutError:
            self.logger.error(msg=f'Time out error')
            return False
