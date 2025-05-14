from typing import Callable

from flask import Flask, abort
from flask_login import current_user, login_required


def set_security_parameters(app: Flask, **params) -> None:
    """
    This func set security params to the app
    :param app: flask.Flask object
    :param params: dict of parameters, which have to be set
    :return: None
    """
    for key, value in params.items():
        app.config[key] = value


def level_required(role: int):
    def decorator(func: Callable):
        @login_required
        def wrap():
            level = current_user.user_level
            if level == role:
                return func()
            abort(403)

        return wrap

    return decorator
