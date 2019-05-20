import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'secret__key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'sqlite3.db')
    #SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:datatron@localhost/yamato'

class ProductionConfig(Config):
    DEBUG = False
