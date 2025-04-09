import logging
from datetime import timedelta
from os import getenv

from flask import Flask, render_template, url_for, make_response, request
from flask_login import login_required
from flask_restful import Api

from api import ListUsers, Menu
from config import set_security_parameters
from data import global_init

app = Flask(__name__)

# set security

set_security_parameters(app,
                        SECRET_KEY=getenv("SECRET_KEY"),
                        SESSION_COOKIE_SECURE=True,
                        REMEMBER_COOKIE_DURATION=timedelta(days=180)
                        )

# set logging settings

logging.basicConfig(filename='logs.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s', level=logging.WARNING)

# Adding resources to an api
api = Api(app)
api.add_resource(ListUsers, '/api/v2/users')
api.add_resource(Menu, '/api/v2/menu')


# error handlers
@app.errorhandler(404)
def not_found(error):
    img_path = url_for('static', filename='img/errors/404_error.png')
    css_path = url_for('static', filename='css/errors.css')
    # TODO: make a template for this error
    logging.critical(error)
    return make_response(render_template('errors/not_found.html',
                                         error=error, img_path=img_path, css_file=css_path,
                                         title='Not Found'),
                         404)


@app.errorhandler(400)
def bad_request():
    return make_response(render_template('errors/bad_request.html', title='Bad request'), 400)


@app.route('/login', methods=['POST', 'GET'])
def authorize():
    return ''


@app.route('/signup', methods=['POST', 'GET'])
def registrate():
    return ''


@login_required
@app.route('/account', methods=['GET'])
def account():
    return render_template(f'{check_agent(request.user_agent)}/account.html', title='Личный кабинет')


def check_agent(agent) -> str:
    # if 'Apple' in agent.string or 'Android' in agent.string:
    #     type_ = 'mobile'
    # else:
    #     type_ = 'desktop'
    return 'desktop' if agent else 'mobile'


@app.route('/', methods=['GET'])
def index():
    css_file = url_for('static', filename='css/style.css')
    type_ = check_agent(request.user_agent)
    return render_template(f"{type_}/base.html", title='Home', css_file=css_file)


if __name__ == '__main__':
    global_init()
    app.run()
