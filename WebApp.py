import asyncio
import logging
from datetime import timedelta
from os import getenv
from typing import Any, Type

import requests
from aiohttp import ClientSession, ClientTimeout
from dotenv import load_dotenv
from flask import (
    Flask, url_for, make_response,
    render_template, redirect, jsonify,
    Blueprint, Response, session, request
)
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
from sqlalchemy import select, Row
from werkzeug.exceptions import HTTPException
from werkzeug.user_agent import UserAgent

from api import ListUsers, MenuList, MenuItem, UserItem, OrderItem, OrderList
from config import set_security_parameters
from data import global_init, create_session, User, Menu, Order
from forms import LoginForm, SignupForm, ChangeUserDataForm  # Import all packages needed


# from flask_security import roles_required, roles_accepted,

class WebApp(Flask):
    """
    This is the main class of the Application, inherited from flask.Flask.
    """

    def __init__(self, name: str):
        super().__init__(name)

        self.login_manager = LoginManager()
        self.login_manager.init_app(self)
        self.setup_login_manager()
        # create and init login_manager

        load_dotenv()
        # load environment

        set_security_parameters(self,
                                SECRET_KEY=getenv("SECRET_KEY"),
                                SESSION_COOKIE_SECURE=True,
                                REMEMBER_COOKIE_DURATION=timedelta(days=180)
                                )
        # set security params of the app

        self.api = Api(self)
        self.set_api_resources()
        # create flask_restful.Api and set resources for it

        self.permanent_session_lifetime = timedelta(days=14)
        # make session permanent for saving users' cart

        logging.basicConfig(filename='logs.log',
                            format='%(asctime)s %(levelname)s %(name)s %(message)s',
                            level=logging.WARNING, filemode='w')
        self.base_logger = logging.getLogger(__name__)
        # set logger and settings for him

        self.admin_blueprint = Blueprint('admin', __name__, template_folder='templates/stuff')
        # create flask.Blueprint for stuff pages of the app

        self._create_routes()
        self._set_error_handlers()
        self._create_admin_blueprint_routes()
        # set all routes needed

        self.register_blueprint(self.admin_blueprint)
        # register blueprint

        self.menu_image_counter = 1

    def _create_admin_blueprint_routes(self) -> None:
        """
        Creates rotes for admin blueprint
        :return: None
        """

        @self.admin_blueprint.route('/stuff/login', methods=['POST', 'GET'])
        def admin_login() -> str | Response:
            """
            shows page  of login if user has not authorized else redirect him to account page
            :return: str or Response
            """
            form = LoginForm()  # create login form
            if form.validate_on_submit():  # validation on success
                expression: Any = (User.email == form.email.data, User.user_level > 1)
                user: User | None = asyncio.run(self.get_db_data(User, expression))  # get user if exists
                if user and user.check_password(form.password.data):  # validate data
                    return redirect('/account')  # Redirect to an account page
                return render_template('stuff/login.html', message='Неверный логин или пароль')
            return render_template('login.html')

        @self.admin_blueprint.route('/admin/base')
        def admin_base():
            return render_template('desktop/admin_index.html')

    def _set_error_handlers(self) -> None:
        """
        Creates error handlers
        :return: None
        """

        # __error_docs = \
        #     "Catch http-error {}\n" \
        #     "param error: HTTPException which was raised\n" \
        #     ":return: status-code and error template"
        #
        # def set_doc(func: Callable) -> Callable:
        #     def wrapp(error: HTTPException) -> Response:
        #         func.__doc__ = __error_docs.format(error.code)
        #         return func(error)
        #
        #     return wrapp

        @self.errorhandler(404)
        def not_found(error: HTTPException) -> Response:
            self.base_logger.critical(error)
            return make_response(
                render_template('errors/not_found.html',
                                error=error, title='Не найдено'), 404
            )

        @self.errorhandler(400)
        def bad_request(error: HTTPException) -> Response:
            return make_response(
                render_template('errors/bad_request.html',
                                title='Ошибка', error=error), 400
            )

        @self.errorhandler(401)
        def unauthorized(error):
            return make_response(
                render_template('errors/unauthorized.html',
                                title='Вы не авторизованы', error=error), 401
            )

        @self.errorhandler(500)
        def server_error(error):
            return make_response(
                render_template('errors/server_error.html',
                                title='Внутренняя ошибка сервера', error=error), 500
            )

    def setup_login_manager(self) -> None:
        """
        Creates func load_user needed for self.login_manager
        :return: None
        """

        async def _load_user(user_id: int) -> User:
            """
            get user from database by user_id
            :param user_id: user identity
            :return: User object
            """
            async with create_session() as db_sess:
                expression: Any = User.id == user_id
                user: Row[User] = (await db_sess.execute(select(User).where(expression))).first()
            return user[0]

        @self.login_manager.user_loader
        def load_user(user_id: int) -> User:
            """
            get result of coroutine _load_user (see docs there)
            :param user_id: user identity
            :return: User
            """
            return asyncio.run(_load_user(user_id))

    def _create_routes(self) -> None:
        """
        Creates routes (functions decorated by self.route method)  for the main app
        :return: None
        """

        @self.route('/menu', methods=['GET'])
        def get_menu():
            menu_ = asyncio.run(self.get_menu_list())
            try:
                cart_ = session['cart']
            except KeyError:
                session['cart'] = {}
                cart_ = session['cart']
            return render_template('desktop/menu.html', menu=menu_, cart=cart_)

        @self.route('/add_dish', methods=['POST', 'GET'])
        def add_dish() -> str | Response:
            if request.method == 'POST':
                name = request.form.get('dish_name')
                description = request.form.get('description')
                file = request.files.get('photo')
                price = request.form.get('price')
                category = request.form.get('category')
                img_src = f'{url_for("static", filename=(src := f"img/dishes/img_{self.menu_image_counter}.png"))}'[1:]
                self.menu_image_counter += 1
                with open(img_src, 'wb') as img:
                    img.write(file.read())
                with requests.post(f'http://{getenv("server")}:{getenv("port")}/api/v2/menu', json={
                    'dish_name': name,
                    'description': description,
                    'img_src': src,
                    'category': category,
                    'price': price
                }) as response:
                    if response.status_code == 200:
                        return redirect('/admin/base')
            return render_template('desktop/add_dish.html')

        @self.route('/cart')
        def cart():
            return render_template('desktop/cart.html')

        @self.route('/login', methods=['POST', 'GET'])
        def authorize():
            form = LoginForm()
            css_file = url_for('static', filename='css/style.css')
            if form.validate_on_submit():
                email = form.email.data
                password = form.password.data
                check = form.remember_me.data
                user = asyncio.run(self.get_db_data(User, expression=(User.email == email)))
                if not user or not user.check_password(password):
                    return render_template('desktop/login.html', title='Авторизация', form=form, css_file=css_file,
                                           message='Неверный логин или пароль')
                login_user(user, remember=check)
                return redirect('/account')
            css_file = url_for('static', filename='css/style.css')
            return render_template('desktop/login.html', title='Авторизация', form=form, css_file=css_file)

        @self.route('/signup', methods=['POST', 'GET'])
        def registrate():
            form = SignupForm()
            if form.validate_on_submit():
                email = form.email.data
                password = form.password.data
                name = form.name.data
                surname = form.surname.data
                sex = form.sex.data
                phone_number = form.phone_number.data
                boolean: Any = (User.email == email)

                user = asyncio.run(self.get_db_data(User, boolean))
                if user is not None:
                    return render_template('desktop/signup.html', title='Регистрация',
                                           message="Пользователь с таким email уже существует", form=form)
                params = {
                    "name": name,
                    "surname": surname,
                    "sex": sex,
                    "email": email,
                    "phone_number": phone_number,
                    "password": password,
                }
                response = requests.post(f'http://{getenv("server")}:{getenv("port")}/api/v2/users', json=params)
                if response.status_code == 200 and response.json().get('error') is None:
                    login_user(asyncio.run(self.get_db_data(User, boolean)))
                    return redirect('/account')
                else:
                    return jsonify(response.json())
            return render_template('desktop/signup.html', title='Регистрация', form=form)

        @self.route('/account', methods=['GET'])
        @login_required
        def account():
            return render_template('desktop/account.html', title='Личный кабинет')

        @self.route('/logout')
        def logout():
            logout_user()
            return redirect('/')

        @self.route('/', methods=['GET'])
        def index():
            # type_ = check_agent(request.user_agent)
            api_key = getenv('JAVASCRIPT_API_KEY')
            return render_template(f"desktop/index.html", title='Home',
                                   API_KEY=api_key)

        @self.route('/change_info', methods=['GET', 'POST'])
        @login_required
        def change_info() -> str | Response:
            """
            Shows a page, where user can change profile data on post
            :return: template or redirect to base page
            """
            form = ChangeUserDataForm()
            if form.validate_on_submit():
                params = {
                    'name': form.name.data if form.name.data else None,
                    'surname': form.surname.data if form.surname.data else None,
                    'phone_number': form.phone_number.data if form.phone_number.data else None,
                }
                if form.password.data:
                    params['password'] = form.password.data
                with requests.put(f'http://{getenv("server")}:{getenv("port")}/api/v2/users/{current_user.id}',
                                  json=params) as response:
                    if response.status_code == 200:
                        return redirect('/account')
                    return response.json()
            return render_template('desktop/change_info.html', form=form)

            # TODO: make relationship with get_menu_list, give it to template, and make functions with users

    def setup(self):

        @self.before_request
        def make_session_permanent():
            session.permanent = True

    def set_api_resources(self) -> None:
        """
        Add resources needed to the Api
        :return: None
        """
        self.api.add_resource(ListUsers, '/api/v2/users')
        self.api.add_resource(MenuList, '/api/v2/menu')
        self.api.add_resource(MenuItem, '/api/v2/menu/<int:id_>')
        self.api.add_resource(UserItem, '/api/v2/users/<int:id_>')
        self.api.add_resource(OrderList, '/api/v2/orders')
        self.api.add_resource(OrderItem, '/api/v2/orders/<int:id_>')

    @staticmethod
    async def get_menu_list() -> dict:
        """
        Get menu from api
        :return: json response from api
        """
        async with ClientSession(timeout=ClientTimeout(total=2)) as session_:
            async with session_.get(f'http://{getenv("server")}:{getenv("port")}/api/v2/menu') as response:
                return await response.json()

    @staticmethod
    def check_agent(agent: UserAgent) -> str:
        # TODO: this method

        """
        check user agent and return type of device (desktop or mobile).
        :param agent: flask.request.user-agent
        :return: Optional
        """
        # if 'Apple' in agent.string or 'Android' in agent.string:
        #     type_ = 'mobile'
        # else:
        #     type_ = 'desktop'
        return 'desktop' if agent else 'mobile'

    def run(
            self,
            host: str | None = None,
            port: int | None = None,
            debug: bool | None = None,
            load_dotenv_: bool = True,
            **options: Any,
    ) -> None:
        asyncio.run(self.global_init())  # init the database before running the app
        super().run(host, port, debug, load_dotenv_, **options)

    @staticmethod
    async def global_init() -> None:
        """
        Init of async database
        :return: None
        """
        return await global_init()

    @staticmethod
    async def get_db_data(class_: Type, expression: Any) -> User | Menu | Order | None:
        """
        Get object of the orm-model "class_" from database selected by "expression"
        :param class_: class of model of db
        :param expression: bool expression like obj.id == id for selecting an object
        :return: Obj
        """
        async with create_session() as session_:
            obj = (await session_.execute(select(class_).where(expression))).first()
        return obj[0] if obj is not None else obj
