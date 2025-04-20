import logging
from datetime import timedelta
from os import getenv
from typing import Any

from dotenv import load_dotenv
from flask import Flask, render_template, url_for, make_response, request, redirect
from flask_login import LoginManager, logout_user, login_required
from flask_restful import Api
from requests import post

from api import ListUsers, MenuList, MenuItem, UserItem
from config import set_security_parameters
from data import global_init, create_session, User
from forms import LoginForm

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
    logging.critical(error)
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
@login_manager.user_loader
def load_user(user_id):
    with create_session() as db_sess:
        return db_sess.get(User, user_id)


@app.route('/login', methods=['POST', 'GET'])
def authorize():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/')
    css_file = url_for('static', filename='css/style.css')
    return render_template('desktop/login.html', title='Авторизация', form=form, css_file=css_file)


@app.route('/signup', methods=['POST', 'GET'])
def registrate():
    css_file = url_for('static', filename='css/style.css')
    return render_template('desktop/base.html', title='Регистрация', css_file=css_file)


@app.route('/account', methods=['GET'])
@login_required
def account():
    return render_template(f'{check_agent(request.user_agent)}/account.html', title='Личный кабинет')


def check_agent(agent) -> str:
    # if 'Apple' in agent.string or 'Android' in agent.string:
    #     type_ = 'mobile'
    # else:
    #     type_ = 'desktop'
    return 'desktop' if agent else 'mobile'


@app.route('/check')
def check_user_api():
    response = post('http://localhost:5000/api/v2/users', json={
        'name': 'Lando',
        'surname': 'Norris',
        'email': 'ageeva_oxana@mail.ru',
        'hashed_password': 'password'
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
    return render_template(f"desktop/base.html", title='Home', css_file=css_file, js_file=js_file, API_KEY=api_key)


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


if __name__ == '__main__':
    global_init()
    app.run()
