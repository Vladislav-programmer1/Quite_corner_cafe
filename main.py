import logging
from datetime import timedelta
from os import getenv

from flask import Flask, render_template, url_for, request, make_response

from config import set_security_parameters
from data import global_init

app = Flask(__name__)
set_security_parameters(app,
                        SECRET_KEY=getenv("SECRET_KEY"),
                        SESSION_COOKIE_SECURE=True,
                        REMEMBER_COOKIE_DURATION=timedelta(days=180)
                        )
logging.basicConfig(filename='logs.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s', level=logging.WARNING)


@app.errorhandler(404)
def not_found(error):
    img_path = url_for('static', filename='img/errors/404_error.png')
    css_path = url_for('static', filename='css/errors.css')
    # TODO: make a template for this error
    logging.critical(error)
    return make_response(render_template('errors/not_found.html', error=error, img_path=img_path, css_file=css_path),
                         404)


@app.route("/authorize")
def authorize():
    pass


@app.route('registration')
def registrate():
    pass


@app.route('/', methods=['GET'])
def index():
    css_file = url_for('static', filename='css/style.css')
    if 'Apple' in request.user_agent.string or 'Android' in request.user_agent.string:
        type_ = 'mobile'
    else:
        type_ = 'desktop'
    return render_template(f"{type_}/base.html", title='Home', css_file=css_file)


if __name__ == '__main__':
    global_init()
    app.run()
