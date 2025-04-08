from flask import Flask


def set_security_parameters(app: Flask, **params) -> None:
    """
    This func set security params to the app
    :param app: flask.Flask object
    :param params: dict of parameters, which have to be set
    :return: None
    """
    for key, value in params.items():
        app.config[key] = value
