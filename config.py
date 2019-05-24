import os
from utils.config import bool_env, str_env, int_env, float_env

# Set those for Heroku configuration
APPLICATION_ENV = str_env('APPLICATION_ENV', 'development')
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def get(name, default=None):
    """
    Get the value of a variable in the settings module scope.
    """
    return globals().get(name, default)


class BaseConfig(object):
    DEBUG = bool_env('DEBUG', True)
    PORT = int_env('PORT', 8001)

    ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
    AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'  # noqa

    AUTHORIZATION_SCOPE = 'openid email profile webmasters.readonly'

    AUTH_REDIRECT_URI = str_env("FN_AUTH_REDIRECT_URI", False)
    BASE_URI = str_env("FN_BASE_URI", False)
    CLIENT_ID = str_env("FN_CLIENT_ID", False)
    CLIENT_SECRET = str_env("FN_CLIENT_SECRET", False)

    AUTH_TOKEN_KEY = 'auth_token'
    AUTH_STATE_KEY = 'auth_state'

    SESSION_SECRET = str_env('SESSION_SECRET', 'delizio')
    SECRET_KEY = str_env('SECRET_KEY', SESSION_SECRET)

    SQLALCHEMY_DATABASE_URI = str_env(
            'DATABASE_URI', 'sqlite:///' + os.path.join(BASE_DIR, 'sqlite3.db')
        )

    BASIC_AUTH_USERNAME = str_env(
        'BASIC_AUTH_USERNAME', 'admin'
    )

    BASIC_AUTH_PASSWORD = str_env(
        'BASIC_AUTH_PASSWORD', 'password'
    )


class DevConfig(BaseConfig):
    # Database connection (Dev)
    AUTH_REDIRECT_URI = "http://localhost:8001/google/auth"
    BASE_URI = "http://localhost:8001"


class StagingConfig(BaseConfig):
    AUTH_REDIRECT_URI = "http://deeperinsights.io/google/auth"
    BASE_URI = "http://deeperinsights.io"
    PORT = 80


class ProdConfig(BaseConfig):
    # Database connection (Prod)
    AUTH_REDIRECT_URI = "http://deeperinsights.io/google/auth"
    BASE_URI = "http://deeperinsights.io"
    DEBUG = False
    PORT = 80


settings = None
if APPLICATION_ENV == 'development':
    settings = DevConfig()
elif APPLICATION_ENV == 'staging':
    settings = StagingConfig()
elif APPLICATION_ENV == 'production':
    settings = ProdConfig()
