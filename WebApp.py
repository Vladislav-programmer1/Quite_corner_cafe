import asyncio
import logging
from datetime import timedelta
from os import getenv
from typing import Any, Type

import requests
from dotenv import load_dotenv
from flask import Flask, url_for, make_response, render_template, redirect, jsonify, Blueprint
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_restful import Api
from requests import post
from sqlalchemy import select

from api import ListUsers, MenuList, MenuItem, UserItem
from api.rest.OrderResource import OrderList, OrderItem
from config import set_security_parameters
from data import global_init, create_session, User
from forms import LoginForm, SignupForm


class WebApp(Flask):
    def __init__(self, name):
        super().__init__(name)
        self.login_manager = LoginManager()
        self.login_manager.init_app(self)
        load_dotenv()
        set_security_parameters(self,
                                SECRET_KEY=getenv("SECRET_KEY"),
                                SESSION_COOKIE_SECURE=True,
                                REMEMBER_COOKIE_DURATION=timedelta(days=180)
                                )
        self.api = Api(self)
        self.set_api_resources()
        logging.basicConfig(filename='logs.log',
                            format='%(asctime)s %(levelname)s %(name)s %(message)s',
                            level=logging.WARNING, filemode='w')
        self.base_logger = logging.getLogger(__name__)
        self.admin_blueprint = Blueprint('admin', __name__, template_folder='templates/stuff')
        self._create_routes()
        self._create_admin_blueprint_routes()
        self.register_blueprint(self.admin_blueprint)

    def _create_admin_blueprint_routes(self):
        @self.admin_blueprint.route('/stuff/login', methods=['POST', 'GET'])
        def admin_login():
            form = LoginForm()
            if form.validate_on_submit():
                with create_session() as session:
                    expression: Any = (User.email == form.email.data, User.user_level > 1)
                    user: User | None = session.query(User).filter(expression).first()
                    if user and user.check_password(form.password.data):
                        return redirect('/account')
                    return render_template('stuff/login.html', message='Неверный логин или пароль')
            return render_template('stuff/login.html')

    def _set_error_handlers(self):
        @self.errorhandler(404)
        def not_found(error):
            img_path = url_for('static', filename='img/errors/404_error.png')
            css_path = url_for('static', filename='css/errors.css')
            self.base_logger.critical(error)
            return make_response(render_template('errors/not_found.html',
                                                 error=error, img_path=img_path, css_file=css_path,
                                                 title='Not Found'),
                                 404)

        @self.errorhandler(400)
        def bad_request(error):
            return make_response(render_template('errors/bad_request.html', title='Bad request', error=error), 400)

        @self.errorhandler(401)
        def unauthorized(error):
            if error:
                pass
            return redirect('/')

        @self.errorhandler(500)
        def server_error(error):
            return make_response(render_template('errors/server_error.html', title='Server error', error=error), 500)

    def _create_routes(self):
        self._set_error_handlers()

        async def _load_user(user_id: int):
            async with create_session() as db_sess:
                expression: Any = User.id == user_id
                user = (await db_sess.execute(select(User).where(expression))).first()
            return user[0]

        @self.login_manager.user_loader
        def load_user(user_id: int):
            return asyncio.run(_load_user(user_id))

        @self.route('/login', methods=['POST', 'GET'])
        def authorize():
            form = LoginForm()
            css_file = url_for('static', filename='css/style.css')
            if form.validate_on_submit():
                email = form.email.data
                password = form.password.data
                check = form.remember_me.data
                user = asyncio.run(self.get_db_data(User, expression=(User.email == email)))
                if not user[0] or not user[0].check_password(password):
                    return render_template('desktop/login.html', title='Авторизация', form=form, css_file=css_file,
                                           message='Неверный логин или пароль')
                login_user(user[0], remember=check)
                return redirect('/account')
            css_file = url_for('static', filename='css/style.css')
            return render_template('desktop/login.html', title='Авторизация', form=form, css_file=css_file)

        @self.route('/signup', methods=['POST', 'GET'])
        def registrate():
            css_file = url_for('static', filename='css/style.css')
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
                if user:
                    return render_template('desktop/signup.html', title='Регистрация', css_file=css_file,
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
                if response.status_code == 200 and not response.json().get('error'):
                    login_user(asyncio.run(self.get_db_data(User, boolean))[0])
                    return redirect('/account')
                else:
                    return jsonify(response.json())
            return render_template('desktop/signup.html', title='Регистрация', css_file=css_file, form=form)

        @self.route('/account', methods=['GET'])
        @login_required
        def account():
            css_file = url_for('static', filename='css/style.css')
            return render_template('desktop/account.html', title='Личный кабинет', css_file=css_file)

        @self.route('/check')
        def check_user_api():
            response = post(f'http://{getenv("server")}:{getenv("port")}/api/v2/users', json={
                'name': 'Lando',
                'surname': 'Norris',
                'email': 'o.chernushina1123@mail.ru',
                'password': 'password',
                'sex': 'М',
                'phone_number': '+79183105698'
            })
            return response.json()

        @self.route('/check2')
        def check_user_api2():
            response = post(f'http://{getenv("server")}:{getenv("port")}/api/v2/users', json={
                'name': 'Lando',
                'surname': 'Norris',
                'email': 'o.chernushina2123@mail.ru',
                'password': 'password',
                'sex': 'М',
                'phone_number': '+79183105698'
            })
            return response.json()

        @self.route('/logout')
        def logout():
            logout_user()
            return redirect('/')

        @self.route('/', methods=['GET'])
        def index():
            # type_ = check_agent(request.user_agent)
            css_file = url_for('static', filename='css/style.css')
            js_file = url_for('static', filename='js/index.js')
            api_key = getenv('JAVASCRIPT_API_KEY')
            return render_template(f"desktop/index.html", title='Home', css_file=css_file, js_file=js_file,
                                   API_KEY=api_key)

        @self.route('/change_info')
        @login_required
        def change_info():
            return render_template('desktop/change_info.html')

    def set_api_resources(self):
        self.api.add_resource(ListUsers, '/api/v2/users')
        self.api.add_resource(MenuList, '/api/v2/menu')
        self.api.add_resource(MenuItem, '/api/v2/menu/<int:item_id>')
        self.api.add_resource(UserItem, '/api/v2/users/<int:user_id>')
        self.api.add_resource(OrderList, '/api/v2/orders')
        self.api.add_resource(OrderItem, '/api/v2/orders/<int:order_id>')

    @staticmethod
    def check_agent(agent) -> str:
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
        asyncio.run(self.global_init())
        super().run(host, port, debug, load_dotenv_, **options)

    @staticmethod
    async def global_init():
        return await global_init()

    @staticmethod
    async def get_db_data(class_: Type, expression: Any):
        async with create_session() as session:
            obj = (await session.execute(select(class_).where(expression))).first()
        return obj
