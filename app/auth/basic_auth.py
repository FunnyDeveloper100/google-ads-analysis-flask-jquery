from flask_basicauth import BasicAuth

basic_auth = BasicAuth()


def init_app(app):
    basic_auth = BasicAuth(app)