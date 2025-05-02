import asyncio
import logging
from datetime import timedelta
from os import getenv
from typing import Any, Type

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, url_for, make_response, redirect, jsonify
from flask_login import LoginManager, logout_user, login_required, login_user
from flask_restful import Api
from requests import post
from sqlalchemy import select

from api import ListUsers, MenuList, MenuItem, UserItem
from config import set_security_parameters
from data import global_init, create_session, User
from forms import LoginForm, SignupForm

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

load_dotenv()

set_security_parameters(app,
                        SECRET_KEY=getenv("SECRET_KEY"),
                        SESSION_COOKIE_SECURE=True,
                        REMEMBER_COOKIE_DURATION=timedelta(days=180)
                        )

logging.basicConfig(filename='logs.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s',
                    level=logging.WARNING, filemode='w')
logger = logging.getLogger(__name__)

api = Api(app)
api.add_resource(ListUsers, '/api/v2/users')
api.add_resource(MenuList, '/api/v2/menu')
api.add_resource(MenuItem, '/api/v2/menu/<int:item_id>')
api.add_resource(UserItem, '/api/v2/users/<int:user_id>')


# TODO: make a templates for the pages
# error handlers
@app.errorhandler(404)
def not_found(error):
    img_path = url_for('static', filename='img/errors/404_error.png')
    css_path = url_for('static', filename='css/errors.css')
    logger.critical(error)
    return make_response(render_template('errors/not_found.html',
                                         error=error, img_path=img_path, css_file=css_path,
                                         title='Not Found'),
                         404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(render_template('errors/bad_request.html', title='Bad request', error=error), 400)


@app.errorhandler(401)
def unauthorized(error):
    if error:
        pass
    return redirect('/')


@app.errorhandler(500)
def server_error(error):
    return make_response(render_template('errors/server_error.html', title='Server error', error=error), 500)


# user loader
async def _load_user(user_id: int):
    async with create_session() as db_sess:
        expression: Any = User.id == user_id
        user = (await db_sess.execute(select(User).where(expression))).first()
    return user[0]


@login_manager.user_loader
def load_user(user_id: int):
    return asyncio.run(_load_user(user_id))


async def get_db_data(class_: Type, expression: Any):
    async with create_session() as session:
        user = (await session.execute(select(class_).where(expression))).first()
    return user


@app.route('/login', methods=['POST', 'GET'])
def authorize():
    form = LoginForm()
    css_file = url_for('static', filename='css/style.css')
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        check = form.remember_me.data
        user = asyncio.run(get_db_data(User, expression=(User.email == email)))
        if not user[0] or not user[0].check_password(password):
            return render_template('desktop/login.html', title='Авторизация', form=form, css_file=css_file,
                                   message='Неверный логин или пароль')
        login_user(user[0], remember=check)
        return redirect('/account')
    css_file = url_for('static', filename='css/style.css')
    return render_template('desktop/login.html', title='Авторизация', form=form, css_file=css_file)


@app.route('/signup', methods=['POST', 'GET'])
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

        user = asyncio.run(get_db_data(User, boolean))
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
            login_user(asyncio.run(get_db_data(User, boolean))[0])
            return redirect('/account')
        else:
            return jsonify(response.json())
    return render_template('desktop/signup.html', title='Регистрация', css_file=css_file, form=form)


@app.route('/account', methods=['GET'])
@login_required
def account():
    css_file = url_for('static', filename='css/style.css')
    return render_template('desktop/account.html', title='Личный кабинет', css_file=css_file)


def check_agent(agent) -> str:
    # if 'Apple' in agent.string or 'Android' in agent.string:
    #     type_ = 'mobile'
    # else:
    #     type_ = 'desktop'
    return 'desktop' if agent else 'mobile'


@app.route('/check')
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


@app.route('/check2')
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


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/', methods=['GET'])
def index():
    # type_ = check_agent(request.user_agent)
    css_file = url_for('static', filename='css/style.css')
    js_file = url_for('static', filename='js/index.js')
    api_key = getenv('JAVASCRIPT_API_KEY')
    return render_template(f"desktop/index.html", title='Home', css_file=css_file, js_file=js_file, API_KEY=api_key)


@app.route('/stuff/login', methods=['POST', 'GET'])
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


@app.route('/change_info')
@login_required
def change_info():
    return render_template('desktop/change_info.html')


async def main():
    await global_init()


if __name__ == '__main__':
    asyncio.run(main())
    app.run(port=getenv('port'), host=getenv('server'))
