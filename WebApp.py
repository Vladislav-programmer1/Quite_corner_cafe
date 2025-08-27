import asyncio
import logging
from datetime import timedelta
from json import loads
from os import getenv
from typing import Any, Type

import requests
from dotenv import load_dotenv
from flask import (
    Flask, url_for, make_response,
    render_template, redirect, jsonify,
    Response, session, request
)
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
from sqlalchemy import select, Row
from werkzeug.exceptions import HTTPException

from ExtraClasses import ApiManager, BlueprintManager
from SMTP import send_email
from data import global_init, create_session, User, Menu, Order
from forms import LoginForm, SignupForm, ChangeUserDataForm  # Import all packages needed
from utils import set_security_parameters


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
        self.ApiManager = ApiManager(self)
        # create flask_restful.Api and set resources for it

        logging.basicConfig(filename='logs.log',
                            format='%(asctime)s %(levelname)s %(name)s %(message)s',
                            level=logging.WARNING, filemode='w')
        self.base_logger = logging.getLogger(__name__)
        # set logger and settings for him

        self.admin_blueprint = BlueprintManager(self.ApiManager, 'admin', __name__,
                                                template_folder='templates/stuff')
        # create flask.Blueprint for stuff pages of the app

        self._create_routes()
        self._set_error_handlers()
        # set all routes needed

        self.register_blueprint(self.admin_blueprint)
        # register blueprint

        self._update_session()
        self.setup()
        # session setup

    def _set_error_handlers(self) -> None:
        """
        Creates error handlers
        :return: None
        """

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

        @self.errorhandler(403)
        def no_rights(error):
            return make_response(render_template('errors/no_rights.html', title='Ошибка уровня доступа', error=error),
                                 403)

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

        @self.route('/policy')
        def get_privacy_policy():
            """
            Gives a page with privacy policy of our website
            :return: file
            """
            return render_template('security.html')

        @self.route('/menu', methods=['GET'])
        def get_menu():
            """
            Rotes menu page
            :return: page
            """
            menu_ = asyncio.run(self.ApiManager.get_api_list('menu'))  # get menu from api
            cart_ = session['cart'] = dict()  # set cart
            return render_template('menu.html', menu=menu_, cart=cart_, title='Меню')

        @self.route('/cart')
        def cart() -> str | Response:
            """
            Cart page.
            :return: page, where user can check his order and confirm it
            """
            if session.get('cart'):
                return render_template('cart.html', session=session, title='Корзина')
            return redirect('/menu')

        @self.route('/checkout')
        @login_required
        def checkout():
            """
            Post user order to db and send him a message
            :return:
            """
            if 'cart' not in session or not session['cart']:
                return redirect('/cart')
            with requests.post(f'http://{getenv("server")}:{getenv("port")}/api/v2/orders', json={
                'price': session.get('total', 0),
                'position_list': ' '.join(
                    [key for key in session.get('cart').keys() if session['cart'][key][2] is not None]),
                'count_list': ' '.join(
                    map(str, [value[2] for value in session.get('cart', dict()).values() if value[2] is not None]))
            }):
                pass
            text = self.get_email_text()
            send_email(current_user.email, 'Ваш заказ готовится', text=text)
            return render_template('checkout.html', title='Заказ готовится')

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
                    return render_template('login.html', title='Авторизация', form=form, css_file=css_file,
                                           message='Неверный логин или пароль')
                login_user(user, remember=check)
                return redirect('/account')
            css_file = url_for('static', filename='css/style.css')
            return render_template('login.html', title='Авторизация', form=form, css_file=css_file)

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
                    return render_template('signup.html', title='Регистрация',
                                           message="Пользователь с таким email уже существует", form=form)
                params = {
                    "name": name,
                    "surname": surname,
                    "sex": sex,
                    "email": email,
                    "phone_number": phone_number,
                    "password": password,
                }
                response = asyncio.run(
                    self.ApiManager.post('users', data=params))
                if response:
                    login_user(asyncio.run(self.get_db_data(User, boolean)))
                    return redirect('/account')
            return render_template('signup.html', title='Регистрация', form=form)

        @self.route('/account', methods=['GET'])
        @login_required
        def account():
            return render_template('account.html', title='Личный кабинет')

        @self.route('/logout')
        def logout():
            logout_user()
            return redirect('/')

        @self.route('/', methods=['GET'])
        def index():
            api_key = getenv('JAVASCRIPT_API_KEY')
            return render_template(f"index.html", title='Home',
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
                    'user_level': current_user.user_level,
                }
                if form.password.data:
                    params['password'] = form.password.data
                if response := asyncio.run(self.ApiManager.put('users', current_user.id, data=params)):
                    return redirect('/account')
                return render_template('change_info.html', form=form, title='Изменение данных',
                                       message='Ошибка при попытке изменения данных, попробуйте снова...')

            return render_template('change_info.html', form=form, title='Изменение данных')

    def _update_session(self) -> None:
        """
        Set methods for updating current session
        :return: None
        """

        @self.route('/update_cart', methods=['POST'])
        def update_cart() -> Response | tuple[bool, Exception]:
            """
            Set order item into cart (into session)
            For JavaScript only
            :return: success
            """
            try:
                data_ = request.get_json()
                value = loads(data_['value'].replace("'", '"').replace("True", 'true').replace('False', 'false'))

                name = value['dish_name']
                price = value['price']
                total = data_['total']
                counter = data_['counter']
                session['cart'] = session.get('cart', dict())
                session['cart'][name] = (name, price, counter)
                session['total'] = total
            except Exception as e:
                return False, e
            return jsonify({'result': 'success'})

    @staticmethod
    def get_email_text() -> str:
        """
        :return: text for email, generated by data in cart
        """
        return '\n'.join(
            [f'{value[0]} - {value[1]} ₽ - {value[2]} шт.' for value in session.get('cart', dict()).values() if
             value[2] is not None]) + f'\nИтого: {session.get("total")}'

    def setup(self):
        """
        Some session setup
        """

        @self.before_request
        def make_session_permanent():
            session.permanent = True

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
